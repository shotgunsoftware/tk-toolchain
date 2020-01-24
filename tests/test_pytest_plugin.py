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


def test_shotgun_repos_root(repos_root):
    """
    Ensure SHOTGUN_REPOS_ROOT is set.
    """
    assert os.environ.get("SHOTGUN_REPOS_ROOT") == repos_root


def test_shotgun_current_repo_root(current_repo_root):
    """
    Ensure SHOTGUN_CURRENT_REPO_ROOT is set.
    """
    assert os.environ.get("SHOTGUN_CURRENT_REPO_ROOT") == current_repo_root


def test_shotgun_test_engine_env_var(current_repo_root):
    """
    Ensure SHOTGUN_TEST_ENGINE is set.
    """
    assert os.environ.get("SHOTGUN_TEST_ENGINE") == os.path.join(
        os.path.join(current_repo_root, "tk_toolchain", "tk_testengine")
    )
