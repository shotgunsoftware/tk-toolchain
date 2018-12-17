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

from .repo import find_repo_root


def is_tk_core(folder):
    root = find_repo_root(folder)
    return os.path.basename(root) == "tk-core"


def is_engine(folder):
    root = find_repo_root(folder)
    return os.path.exists(os.path.join(root, "engine.py"))


def is_framework(folder):
    root = find_repo_root(folder)
    return os.path.exists(os.path.join(root, "framework.py"))


def is_config(folder):
    root = find_repo_root(folder)
    return os.path.basename(root).startswith("tk-config")


def is_app(folder):
    root = find_repo_root(folder)
    return os.path.basename(root).startswith("app.py")
