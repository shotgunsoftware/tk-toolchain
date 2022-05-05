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

import os
import sys
import shutil
import tempfile


def execute_command(log, command, expected_code=0):
    """
    Helper. executes shell command and raises exception
    if return code is nonzero
    """
    if log:
        log.info("[CMD: %s]" % command)
    ret = os.system(command)
    if ret != expected_code:
        raise Exception("Command returned Error code %s - aborting!" % ret)
    if log:
        log.debug("Command %s executed successfully." % command)


class SphinxProcessor(object):
    """
    Class that wraps sphinx doc generation
    """

    def __init__(self, core_path, path, log, additional_paths=None):
        """
        :param core_path: Path to tk-core. If None, the core API will
                          not be added to the pythonpath.
        :param path: Path to the app/engine/fw to document
        :param log: Logger
        :param additional_paths: Additional file paths to prepend to the PYTHONPATH and sys.path
        """
        self._log = log
        self._path = path

        self._log.debug("Starting Sphinx processor for %s..." % path)

        self._docs_path = os.path.join(path, "docs")

        if not os.path.exists(os.path.join(self._docs_path, "index.rst")):
            # fall back on "docs_src"
            log.warning(
                "No docs found in 'docs' folder - falling back on 'doc_src' folder"
            )
            self._docs_path = os.path.join(path, "doc_src")
            if not os.path.exists(os.path.join(self._docs_path, "index.rst")):
                raise Exception("Cannot find a docs folder in %s!" % path)

        # now add stuff to pythonpath
        # note that we are adding it to both sys.path and the
        # PYTHONPATH so that it gets picked up by the doc gen script
        # later on.

        # add core API
        if core_path:
            self._add_to_pythonpath(os.path.join(core_path, "python"))

        # add main bundle location
        self._add_to_pythonpath(path)

        # add all bundle subfolders - ignore hidden items (those that start with '.') and
        # ignore the specified list of folders that we know we won't need to generate docs from
        ignore_folders = ["__pycache__", "docs", "tests", "resources"]
        bundle_items = os.listdir(path)
        for item_name in bundle_items:
            if (
                os.path.isdir(os.path.join(path, item_name))
                and item_name not in ignore_folders
                and not item_name.startswith(".")
            ):
                self._add_to_pythonpath(os.path.join(path, item_name))

        # add any additional paths specified
        additional_paths = additional_paths or []
        for additional_path in additional_paths:
            self._add_to_pythonpath(additional_path)

        # check that Sphinx and PySide are available
        if core_path:
            try:
                import sgtk  # noqa
            except ImportError:
                raise Exception("Cannot import sgtk. Please add to pythonpath")

        # make a temp folder for building docs
        self._sphinx_build_dir = os.path.join(
            tempfile.gettempdir(), "sphinx-build", os.path.basename(path)
        )
        self._log.debug("Sphinx will build into %s..." % self._sphinx_build_dir)

        # get a path to conf.py
        this_folder = os.path.abspath(os.path.dirname(__file__))
        self._sphinx_conf_py_location = os.path.join(this_folder, "sphinx_data")
        self._log.debug(
            "Sphinx will use configuration from %s..." % self._sphinx_conf_py_location
        )

    def _add_to_pythonpath(self, path):
        """
        Prepends to PYTHONPATH and sys.path

        :param path: The path to add
        """
        pythonpath = os.environ.get("PYTHONPATH", "").split(os.path.pathsep)
        path = os.path.expanduser(os.path.expandvars(path))
        pythonpath.insert(0, path)
        sys.path.insert(0, path)
        self._log.debug("Added to PYTHONPATH: %s" % path)
        os.environ["PYTHONPATH"] = os.path.pathsep.join(pythonpath)

    def build_docs(
        self, name, version, warnings_as_errors=True, additional_static_paths=None
    ):
        """
        Generate sphinx docs

        :param name: The name to give to the documentation
        :param version: The version number to associate with the documentation
        :param additional_static_paths: Additional static paths to add to the build output.
        :returns: Path to the built docs
        """
        self._log.debug("Building docs with name %s and version %s" % (name, version))

        # Pass a flag that will cause it to raise an error if a warning is thrown
        # only if warning_as_errors is true. Typically we want this to be always True
        # but we have some repos that need fixing and are currently throwing warnings.
        warnings_as_errors_flag = "-W" if warnings_as_errors else ""

        # run build command
        # Use double quotes to make sure it works on Windows and Unix.
        # -T means show traceback
        cmd = (
            '%s -m sphinx -c "%s" %s -T -E -D project="%s" -D release="%s" -D version="%s" "%s" "%s"'
            % (
                sys.executable,
                self._sphinx_conf_py_location,
                warnings_as_errors_flag,
                name,
                version,
                version,
                self._docs_path,
                self._sphinx_build_dir,
            )
        )

        execute_command(self._log, cmd)

        # make sure there is a .nojekyll file in the github repo, otherwise
        # folders beginning with an _ will be ignored
        no_jekyll = os.path.join(self._sphinx_build_dir, ".nojekyll")

        # Creating .nojekyll file. This is cross platform. os.touch is not.
        with open(no_jekyll, "wt"):
            pass

        # Copy additional static files to the build output
        additional_static_paths = additional_static_paths or []
        # Get the build output dir for html static files. This is the folder defined in conf.py
        # as the html_static_path ("_static").
        static_path_build_dir = os.path.join(self._sphinx_build_dir, "_static")
        for static_path in additional_static_paths:
            self.copy_docs(self._log, static_path, static_path_build_dir)

        return self._sphinx_build_dir

    def copy_docs(self, log, src, dst):
        """
        Alternative implementation to shutil.copytree
        Copies recursively with very open permissions.
        Creates folders if they don't already exist.

        :param src: Source path
        :param dst: Destination path
        """
        if not os.path.exists(dst):
            log.debug("mkdir 0777 %s" % dst)
            os.mkdir(dst, 0o777)

        names = os.listdir(src)
        for name in names:

            srcname = os.path.join(src, name)
            dstname = os.path.join(dst, name)

            try:
                if os.path.isdir(srcname):
                    self.copy_docs(log, srcname, dstname)
                else:
                    shutil.copy(srcname, dstname)
                    log.debug("Copy %s -> %s" % (srcname, dstname))
            except Exception as e:
                log.error("Can't copy %s to %s: %s" % (srcname, dstname, e))
