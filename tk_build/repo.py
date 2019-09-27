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
    @classmethod
    def find_root(cls, path=None):
        path = path or os.getcwd()
        while path and not cls._is_repo_root(path):
            path = os.path.dirname(path)

        # TODO: Add check for when there is no repo root!
        return path

    def __init__(self, path):
        self._root = self.find_root(path)
        # Ensure the repository object is pointing to a valid repo type.
        if (
            self.is_tk_core()
            or self.is_tk_build()
            or self.is_python_api()
            or self.is_bundle()
        ):
            return
        raise RuntimeError("Unexpected repository layout at {0}".format(self._root))

    @property
    def root(self):
        return self._root

    def is_tk_core(self):
        return self._folder_contains("_core_upgrader.py")

    def is_engine(self):
        return self._folder_contains("engine.py")

    def is_framework(self):
        return self._folder_contains("framework.py")

    def is_app(self):
        return self._folder_contains("app.py")

    def is_config(self):
        return os.path.basename(self._root).startswith("tk-config")

    def is_bundle(self):
        return (
            self.is_engine() or self.is_framework() or self.is_app() or self.is_config()
        )

    def is_tk_build(self):
        return self._folder_contains("pytest_tk_build")

    def is_python_api(self):
        return self._folder_contains("shotgun_api3")

    def _folder_contains(self, filename):
        return os.path.exists(os.path.join(self._root, filename))

    @classmethod
    def _is_repo_root(cls, path):
        files = os.listdir(path)
        for repo in [".git", ".svn", ".hg"]:
            if repo in files:
                return True
        return False
