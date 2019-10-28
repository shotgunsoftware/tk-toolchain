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

CURRENT_REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
REPOS_ROOT = os.path.dirname(CURRENT_REPO_ROOT)


def test_shotgun_repos_root():
    """
    Ensure SHOTGUN_REPOS_ROOT is set.
    """
    assert os.environ.get("SHOTGUN_REPOS_ROOT") == REPOS_ROOT


def test_shotgun_current_repo_root():
    """
    Ensure SHOTGUN_CURRENT_REPO_ROOT is set.
    """
    assert os.environ.get("SHOTGUN_CURRENT_REPO_ROOT") == CURRENT_REPO_ROOT


def test_shotgun_test_engine_env_var():
    """
    Ensure SHOTGUN_TEST_ENGINE is set.
    """
    assert os.environ.get("SHOTGUN_TEST_ENGINE") == os.path.join(
        os.path.join(CURRENT_REPO_ROOT, "tk_toolchain", "tk_testengine")
    )
