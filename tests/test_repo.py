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

import pytest
import os


from tk_toolchain.repo import Repository

CURRENT_REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
REPOS_ROOT = os.path.dirname(CURRENT_REPO_ROOT)


def test_find_root():
    """
    Ensure we can find a root.
    """
    # Make sure we can resolve from the current working directly.
    assert Repository.find_root() == CURRENT_REPO_ROOT
    # Make sure we can resolve from any subdirectory
    assert Repository.find_root(os.path.dirname(__file__)) == CURRENT_REPO_ROOT

    with pytest.raises(RuntimeError):
        Repository.find_root("/var/tmp")


def test_repo_init():
    """
    Ensure we can create a repository from a folder.
    """
    assert Repository().root == CURRENT_REPO_ROOT
    # Make sure we can resolve from any subdirectory
    assert Repository(os.path.dirname(__file__)).root == CURRENT_REPO_ROOT
    with pytest.raises(RuntimeError):
        Repository("/var/tmp")


def test_repo_parent():
    assert Repository().parent == REPOS_ROOT


def test_repo_name():
    assert Repository().name == "tk-toolchain"
