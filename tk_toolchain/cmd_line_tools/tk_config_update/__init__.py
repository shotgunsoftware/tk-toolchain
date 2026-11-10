#!/usr/bin/env python
# Copyright (c) 2019 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import argparse
import atexit
import json
import os
import re
import shutil
import subprocess
import tempfile
import textwrap
import urllib.error
import urllib.request

from ruamel import yaml


# FIXME: Maybe we should rename the other repository class (tk_toolchain.repo.Repository)
# to Bundle?
class Repository:
    """
    Handles operations on a repository.
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

    @property
    def current_branch(self):
        """
        Name of the branch currently checked out.
        """
        return self._git_output("rev-parse", "--abbrev-ref", "HEAD").strip()

    def checkout_new_branch(self, branch):
        """
        Create a branch from the current head and switch to it.

        :param str branch: Name of the branch to create.
        """
        self._git("checkout", "-b", branch)

    def remote_branch_exists(self, branch):
        """
        Check if a branch exists on the remote.

        :param str branch: Name of the branch to look for.

        :returns: True if the branch exists on origin, False otherwise.
        """
        output = self._git_output("ls-remote", "--heads", "origin", branch)
        return bool(output.strip())

    def push(self, branch):
        """
        Push a branch back to the remote. This never forces the push.

        :param str branch: Name of the branch to push.
        """
        self._git("push", "origin", branch)

    def diff(self):
        """
        Diff with the head.
        """
        self._git("diff", "HEAD")

    def _git(self, *args):
        """
        Run a git command.

        :param args: List of arguments for the git command.

        If invoking the method as _git("push", "origin", "my-branch"), then the
        result would be subprocess.check_call(["git", "push", "origin", "my-branch"])
        """
        subprocess.check_call(
            ["git"] + list(args), cwd=self._root, env=self._git_environ()
        )

    def _git_environ(self):
        """
        Environment to run git commands in.
        """
        # Disable the pager, we don't want this call to be blocking.
        environ = os.environ.copy()
        environ["PAGER"] = ""
        return environ

    def _git_output(self, *args):
        """
        Run a git command and return its standard output.

        :param args: List of arguments for the git command.

        :returns: The standard output of the command, as a string.
        """
        return subprocess.check_output(
            ["git"] + list(args),
            cwd=self._root,
            env=self._git_environ(),
            text=True,
        )


def enumerate_yaml_files(root):
    """
    Enumerate all the files in the repository.

    :param str root: Path to the repository/

    :returns: Iterator on all files ending with .yml.
    """
    for dirpath, _, filenames in os.walk(root):
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
    and the versions are different.

    Note that for frameworks, a match will occur only if the major version
    is the same.
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
    Update files in the repository that contain a descriptor
    to the given bundle.

    :param str repo_root: Root of the repository to update.
    :param str bundle: Name of the bundle to search for.
    :param str version: Name of the new version.

    :returns: Generator of modified files.
    """
    # For every yml file in the repo
    for yml_file in enumerate_yaml_files(repo_root):
        # Load it and preserve the formatting
        with open(yml_file, "r") as fh:
            _yaml = yaml.YAML()
            yaml_data = _yaml.load(fh)

        # If we found a descriptor to update
        if update_yaml_data(yaml_data, bundle, version):
            # Write back the changes and update the git index.
            with open(yml_file, "w") as fh:
                _yaml = yaml.YAML()
                _yaml.default_flow_style = False
                _yaml.width = 500
                _yaml.dump(yaml_data, fh)
            yield yml_file


GITHUB_API_URL = "https://api.github.com"

# Environment variable holding the GitHub token. This is the same one the git
# credential helper configured by tk-ci-tools uses to push.
GH_ACCESS_TOKEN = "GH_ACCESS_TOKEN"

# Anchored on both ends so only github.com itself matches, not lookalike hosts
# (e.g. notgithub.com) or URLs merely containing "github.com" in their path.
_GITHUB_URL_REGEX = re.compile(
    r"^(?:https://(?:[^@/]+@)?|git@|ssh://git@)"
    r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?/?$"
)


def parse_github_url(url):
    """
    Extract the owner and the name of a repository from a GitHub remote URL.

    Supports https://github.com/owner/repo.git, git@github.com:owner/repo.git and
    ssh://git@github.com/owner/repo.git. Any other host is rejected.

    :param str url: URL of the remote.

    :returns: Tuple of (owner, repository name).

    :raises ValueError: If the URL is not a GitHub repository URL.
    """
    match = _GITHUB_URL_REGEX.match(url)
    if not match:
        raise ValueError("'{0}' is not a GitHub repository URL.".format(url))
    return match.group("owner"), match.group("repo")


def create_pull_request(owner, repo, token, title, head, base, body):
    """
    Open a pull request on GitHub.

    :param str owner: Owner of the repository.
    :param str repo: Name of the repository.
    :param str token: GitHub token allowed to open pull requests.
    :param str title: Title of the pull request.
    :param str head: Branch containing the changes.
    :param str base: Branch the changes should be merged into.
    :param str body: Description of the pull request.

    :returns: URL of the pull request.

    :raises RuntimeError: If GitHub refuses to open the pull request.
    """
    request = urllib.request.Request(
        "{0}/repos/{1}/{2}/pulls".format(GITHUB_API_URL, owner, repo),
        data=json.dumps(
            {"base": base, "body": body, "head": head, "title": title}
        ).encode("utf-8"),
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": "Bearer {0}".format(token),
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request) as response:
            return json.load(response)["html_url"]
    except urllib.error.HTTPError as e:
        # Only report what GitHub told us, never the request, so the token
        # can't leak in the logs.
        raise RuntimeError(
            "Failed to open pull request on {0}/{1} ({2}): {3}".format(
                owner, repo, e.code, e.read().decode("utf-8", "replace")
            )
        ) from e


####################################################################################
# script entry point
def main(arguments=None):
    """
    This will launch all the Toolkit applications and panels registered at app init
    and wait until all of them have been closed.
    """

    parser = argparse.ArgumentParser(
        prog="tk_config_update",
        description=textwrap.dedent("""
            Toolkit Configuration Update

            Update the version of a bundle in a config to the specified version,
            pushes the change to a new branch and opens a pull request.
            """),
        epilog=textwrap.dedent("""
            Example:
                tk-config-update git@github.com:shotgunsoftware/tk-config-default2.git tk-core v0.19.0
            """),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "config",
        help="URL to the TK config git repository to update",
    )

    parser.add_argument(
        "bundle",
        help="Name of the TK component",
    )

    parser.add_argument(
        "version",
        help="Version of the TK component",
    )

    parser.add_argument(
        "--push-changes",
        help="""
            Pushes the changes to a new branch and opens a pull request against
            the default branch. Requires the GH_ACCESS_TOKEN environment variable.
            If not specified, the remote repository is not updated.
        """,
        action="store_true",
        default=False,
    )

    args = parser.parse_args(args=arguments)

    # Fail early if we know we won't be able to open the pull request.
    if args.push_changes is True:
        owner, repo_name = parse_github_url(args.config)
        token = os.environ.get(GH_ACCESS_TOKEN)
        if not token:
            raise RuntimeError(
                "The {0} environment variable is required with --push-changes.".format(
                    GH_ACCESS_TOKEN
                )
            )

    repo = Repository.clone(args.config)
    base_branch = repo.current_branch

    files_updated = []

    for yml_file in update_files(repo.root, args.bundle, args.version):
        print("Updated '{0}'".format(yml_file))
        repo.add(yml_file)
        files_updated.append(yml_file)

    # If the repository was not updated, we're done.
    if not files_updated:
        print("No files were updated.")
        return 0

    repo.diff()

    # Changes are never committed to the base branch directly, they go through
    # a pull request.
    branch = "update/{0}-{1}".format(args.bundle, args.version)
    repo.checkout_new_branch(branch)

    release_notes = (
        "Release notes: https://github.com/shotgunsoftware/{bundle}/releases/tag/{version}"
    ).format(bundle=args.bundle, version=args.version)
    title = "Updated {0} to {1}".format(args.bundle, args.version)

    # Commit the repo and link to the release notes in the comments.
    repo.commit("{0}\n{1}".format(title, release_notes))

    # This script does not upload changes by default.
    if args.push_changes is True:
        # We never force push, so if the branch is already there (e.g. a previous
        # run) a human needs to look at it.
        if repo.remote_branch_exists(branch):
            raise RuntimeError(
                "Branch '{0}' already exists on {1}/{2}. Close the pull request "
                "and delete the branch if it is stale, then run this again.".format(
                    branch, owner, repo_name
                )
            )
        repo.push(branch)
        pull_request_url = create_pull_request(
            owner,
            repo_name,
            token,
            title,
            head=branch,
            base=base_branch,
            body=release_notes,
        )
        print("Opened pull request {0}".format(pull_request_url))
    else:
        print("Specify --push-changes to update the remote repository.")

    return 0
