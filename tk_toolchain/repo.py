# -*- coding: utf-8 -*-
# Copyright (c) 2018 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.


import os


class Repository(object):
    """
    This class allows to introspect the repository.
    """

    @classmethod
    def find_root(cls, path=None):
        """
        Find the root of a repository for a given path inside it.

        :param str path: One of the descendant folders.

        :returns: Path to the repository root.
        """

        child_path = path or os.getcwd()

        # While we haven't reached the root.
        while not cls._is_repo_root(child_path):
            # Peel off one folder from the path.
            parent_path = os.path.dirname(child_path)

            # If the path hasn't changed, we've reached the root of the filesystem.
            if child_path == parent_path:
                raise RuntimeError("{0} is not inside a repository".format(path))

            child_path = parent_path

        return child_path

    def __init__(self, path=None):
        """
        :param str path: Path inside a repository.
        """
        self._root = self.find_root(path)
        # Ensure the root is pointing to a valid repository type.
        if (
            self.is_tk_toolchain()
            or self.is_python_api()
            or self.is_toolkit_component()
        ):
            return

    def __repr__(self):
        """
        Representation of this object.
        """
        return "<{}.{} for {}>".format(
            self.__class__.__module__, self.__class__.__name__, self._root
        )

    @property
    def root(self):
        """
        The root of the repository.
        """
        return self._root

    @property
    def parent(self):
        """
        Parent folder of this repo.
        """
        return os.path.dirname(self.root)

    @property
    def name(self):
        """
        Name of this repo.
        """
        return os.path.basename(self.root)

    def is_tk_core(self):
        """
        Check if the repository is the tk-core repository.

        :returns: ``True`` is the repository is for tk-core, ``False`` otherwise.
        """
        return self._folder_contains("_core_upgrader.py")

    def is_engine(self):
        """
        Check if the repository is for an engine.

        :returns: ``True`` is the repository is for an engine, ``False`` otherwise.
        """
        return self._folder_contains("engine.py")

    def is_framework(self):
        """
        Check if the repository is for a framework.

        :returns: ``True`` is the repository is for a framework, ``False`` otherwise.
        """
        return self._folder_contains("framework.py")

    def is_app(self):
        """
        Check if the repository is for an application.

        :returns: ``True`` is the repository is for an application, ``False`` otherwise.
        """
        return self._folder_contains("app.py")

    def is_config(self):
        """
        Check if the repository is for a configuration.

        :returns: ``True`` is the repository is for a configuration, ``False`` otherwise.
        """
        return self.name.startswith("tk-config")

    def is_toolkit_component(self):
        """
        Check if the repository is for a Toolkit component.

        This can be an engine, framework, app, config or the Toolkit core.

        :returns: ``True`` is the repository is for Toolkit component, ``False`` otherwise.
        """
        return (
            self.is_engine()
            or self.is_framework()
            or self.is_app()
            or self.is_config()
            or self.is_tk_core()
        )

    def is_tk_toolchain(self):
        """
        Check if the repository is for tk-toolchain.

        :returns: ``True`` is the repository is for tk-toolchain, ``False`` otherwise.
        """
        return self._folder_contains("pytest_tank_test")

    def is_python_api(self):
        """
        Check if the repository is for the Python API

        :returns: ``True`` is the repository is for the Python API, ``False`` otherwise.
        """
        return self._folder_contains("shotgun_api3")

    def _folder_contains(self, filename):
        """
        Check if a given file is under the root.

        :param str filename: File to look for.

        :returns: ``True`` is the file was found under the root, ``False`` otherwise.
        """
        return os.path.exists(os.path.join(self._root, filename))

    @classmethod
    def _is_repo_root(cls, path):
        """
        Check if a path is at the root of the repository.

        A path is considered at the root of a repository if the folder contains
        a .git, .svn or .hg folder.

        :returns: ``True`` if the folder is the root of a repository, ``False`` otherwise.
        """
        files = os.listdir(path)
        for source_control_folder in [".git", ".svn", ".hg"]:
            if source_control_folder in files:
                return True
        return False
