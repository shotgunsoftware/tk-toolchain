#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2019 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Toolkit Configuration Update

Update the version of a bundle in a config to the specified version and pushes
it back to the source repository.

Usage:
    tk-config-update <config> <bundle> <version> [--push-changes]

Options:
    --push-changes  Pushes the changes to the repository. If not specified,
                    the remote repository is not updated.

Example:
    tk-config-update git@github.com:shotgunsoftware/tk-config-default2.git tk-core v0.19.0
"""

import subprocess
import sys
import os
import shutil
import atexit
import tempfile
import docopt

try:
    from ruamel import yaml
except ImportError:
    sys.exit("This tool can only be run with Python 2.7 or greater.")


# FIXME: Maybe we should rename the other repository class (tk_toolchain.repo.Repository)
# to Bundle?
class Repository(object):
    """
    Allows to make operations on a repository.
    """

    @classmethod
    def clone(cls, remote):
        """
        Clone a repository from a remote.
        """
        root = tempfile.mkdtemp()
        atexit.register(lambda: shutil.rmtree(root))
        subprocess.check_call(["git", "clone", remote, root, "--depth", "1"])
        return Repository(root)

    def __init__(self, root):
        """
        :param str root: Root of the repository.
        """
        self._root = root

    @property
    def root(self):
        """
        Root of the repository.
        """
        return self._root

    def add(self, location):
        """
        Add a location to the index.

        :param str location: Location on disk.
        """
        self._git("add", location)

    def commit(self, msg):
        """
        Commit the index.

        :param str msg: Message for the commit.
        """
        self._git("commit", "-m", "{0}".format(msg))

    def push(self):
        """
        Push the repository back to the remote.
        """
        self._git("push", "origin", "master")

    def diff(self):
        """
        Diff with the head.
        """
        self._git("diff", "HEAD")

    def _git(self, *args):
        """
        Run a git command.

        :param args: List of arguments for the git command.

        If invoking the method as _git("push", "origin", "master"), then the
        result would be subprocess.check_call(["git", "push", "origin", "master"])
        """
        # Disable the pager, we don't want this call to be blocking.
        environ = os.environ.copy()
        environ["PAGER"] = ""
        subprocess.check_call(["git"] + list(args), cwd=self._root, env=environ)


def enumerate_yaml_files(root):
    """
    Enumerate all the files in the repository.

    :param str root: Path to the repository/

    :returns: Iterator on all files ending with .yml.
    """
    for (dirpath, _, filenames) in os.walk(root):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if filepath.endswith(".yml"):
                yield filepath


def is_app_store_descriptor(data):
    """
    Check if the dictionary is a descriptor.

    :param dict-like data: Dictionary to inspect.

    :returns: True the dictionary has keys type, name and version, False otherwise.
    """
    return (
        data.get("type") == "app_store"
        and "name" in data.keys()
        and "version" in data.keys()
    )


def is_descriptor_matching(data, bundle, version):
    """
    Check if the descriptor that is passed in matches the bundle name
    and potential new version.
    """
    # If this is not the right bundle or the version hasn't changed, skip
    # the update.
    if data["name"] != bundle or data["version"] == version:
        return False

    # Frameworks can be found multiple times in a configuration with different
    # major versions. We must be careful to only update the right one however.
    # To do this, we'll make sure that the major version of the descriptor
    # is the same as the new version's.
    if bundle.startswith("tk-framework"):
        major_released, _ = data["version"].split(".", 1)
        major_update, _ = version.split(".", 1)
        if major_released != major_update:
            return False

    # All good, we can push now.
    return True


def update_yaml_data(data, bundle, version):
    """
    Recursively visit a dictionary looking for a descriptor and updates them
    if there's a match.

    :param dict-like data: Data to visit.
    :param str bundle: Name of the bundle to search for.
    :param str version: New version of the bundle.
    """
    if not isinstance(data, yaml.comments.CommentedMap):
        return False

    file_updated = False

    if is_app_store_descriptor(data):
        # If we've found the bundle and we have a new version
        if is_descriptor_matching(data, bundle, version):
            data["version"] = version
            file_updated = True
    else:
        for value in data.values():
            if update_yaml_data(value, bundle, version):
                file_updated = True

    return file_updated


def update_files(repo_root, bundle, version):
    """
    """
    # For every yml file in the repo
    for yml_file in enumerate_yaml_files(repo_root):

        # Load it and preserve the formatting
        with open(yml_file, "r") as fh:
            yaml_data = yaml.load(fh, yaml.RoundTripLoader)

        # If we found a descriptor to update
        if update_yaml_data(yaml_data, bundle, version):

            # Write back the changes and update the git index.
            with open(yml_file, "w") as fh:
                yaml.dump(
                    yaml_data, fh, default_flow_style=False, Dumper=yaml.RoundTripDumper
                )
            yield yml_file


####################################################################################
# script entry point
def main(arguments=None):
    """
    This will launch all the Toolkit applications and panels registered at app init
    and wait until all of them have been closed.
    """
    arguments = arguments or sys.argv[1:]

    # docopt does not care about the script name, so skip or we'll
    # get an error.
    options = docopt.docopt(__doc__, argv=arguments)

    repo = Repository.clone(options["<config>"])
    bundle = options["<bundle>"]
    version = options["<version>"]

    files_updated = []

    for yml_file in update_files(repo.root, bundle, version):
        print("Updated '{0}'".format(yml_file))
        repo.add(yml_file)
        files_updated.append(yml_file)

    # If the repository was not updated, we're done.
    if not files_updated:
        print("No files were updated.")
        return 0

    repo.diff()

    # Commit the repo and link to the release notes in the comments.
    repo.commit(
        (
            "Updated {bundle} to {version}\n"
            "Release notes: https://github.com/shotgunsoftware/{bundle}/wiki/Release-Notes#{version_no_dots}"
        ).format(
            bundle=bundle, version=version, version_no_dots=version.replace(".", "")
        )
    )

    # This script does not upload changes by default.
    if options["--push-changes"] is True:
        repo.push()
    else:
        print("Specify --push-changes to update the remote repository.")

    return 0
