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

import pytest


@pytest.fixture
def current_repo_root():
    return os.path.dirname(os.path.dirname(__file__))


@pytest.fixture
def repos_root(current_repo_root):
    return os.path.dirname(current_repo_root)


@pytest.fixture
def tk_config_root(repos_root):
    return os.path.join(repos_root, "tk-config-basic")


@pytest.fixture
def tk_core_root(repos_root):
    return os.path.join(repos_root, "tk-core")


@pytest.fixture
def tk_app_root(repos_root):
    return os.path.join(repos_root, "tk-multi-publish2")


@pytest.fixture
def tk_engine_root(repos_root):
    return os.path.join(repos_root, "tk-maya")


@pytest.fixture
def tk_framework_root(repos_root):
    return os.path.join(repos_root, "tk-framework-shotgunutils")


@pytest.fixture
def python_api_root(repos_root):
    return os.path.join(repos_root, "python-api")
