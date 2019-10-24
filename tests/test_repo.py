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

TK_CORE_ROOT = os.path.join(REPOS_ROOT, "tk-core")
TK_FRAMEWORK_ROOT = os.path.join(REPOS_ROOT, "tk-framework-shotgunutils")
TK_APP_ROOT = os.path.join(REPOS_ROOT, "tk-multi-publish2")
TK_ENGINE_ROOT = os.path.join(REPOS_ROOT, "tk-maya")
TK_CONFIG_ROOT = os.path.join(REPOS_ROOT, "tk-config-basic")
PYTHON_API_ROOT = os.path.join(REPOS_ROOT, "python-api")


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
    """
    Ensure repo parent folder is detected properly.
    """
    assert Repository().parent == REPOS_ROOT


def test_repr():
    """
    Ensure __repr__ behaves correctly.
    """
    assert repr(Repository()) == "<tk_toolchain.repo.Repository for {}>".format(
        CURRENT_REPO_ROOT
    )


def test_repo_name():
    """
    Ensure repo name is detected correctly.
    """
    assert Repository().name == "tk-toolchain"


def _test_component(
    repo,
    is_tk_core=False,
    is_framework=False,
    is_config=False,
    is_app=False,
    is_engine=False,
    is_python_api=False,
    is_tk_toolchain=False,
):
    """
    Ensure a given repo object is detected as the right type and that type only.
    """
    assert repo.is_tk_core() == is_tk_core
    assert repo.is_framework() == is_framework
    assert repo.is_app() == is_app
    assert repo.is_engine() == is_engine
    assert repo.is_config() == is_config
    assert repo.is_python_api() == is_python_api
    assert repo.is_tk_toolchain() == is_tk_toolchain

    if is_python_api or is_tk_toolchain:
        assert repo.is_toolkit_component() is False
    else:
        assert repo.is_toolkit_component()


def test_is_tk_core():
    """
    Ensure tk-core repo is detected as such.
    """
    _test_component(Repository(TK_CORE_ROOT), is_tk_core=True)


def test_is_framework():
    """
    Ensure framework repo is detected as such.
    """
    _test_component(Repository(TK_FRAMEWORK_ROOT), is_framework=True)


def test_is_engine():
    """
    Ensure engine repo is detected as such.
    """
    _test_component(Repository(TK_ENGINE_ROOT), is_engine=True)


def test_is_app():
    """
    Ensure app repo is detected as such.
    """
    _test_component(Repository(TK_APP_ROOT), is_app=True)


def test_is_config():
    """
    Ensure config repo is detected as such.
    """
    _test_component(Repository(TK_CONFIG_ROOT), is_config=True)


def test_is_python_api():
    """
    Ensure python-api repo is detected as such.
    """
    _test_component(Repository(PYTHON_API_ROOT), is_python_api=True)
