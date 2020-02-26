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


def test_find_root(current_repo_root, tmpdir):
    """
    Ensure we can find a root.
    """
    # Make sure we can resolve from the current working directly.
    assert Repository.find_root() == current_repo_root
    # Make sure we can resolve from any subdirectory
    assert Repository.find_root(os.path.dirname(__file__)) == current_repo_root

    with pytest.raises(RuntimeError) as exception:
        Repository(tmpdir.strpath)
    assert "is not inside a repository" in str(exception)


def test_repo_init(current_repo_root):
    """
    Ensure we can create a repository from a folder.
    """
    assert Repository().root == current_repo_root
    # Make sure we can resolve from any subdirectory
    assert Repository(os.path.dirname(__file__)).root == current_repo_root


def test_get_environment_variables(current_repo_root, repos_root):
    """
    Ensure environement variables are properly set.
    """
    assert Repository().get_roots_environment_variables() == {
        "SHOTGUN_CURRENT_REPO_ROOT": current_repo_root,
        "SHOTGUN_REPOS_ROOT": repos_root,
    }


def test_repo_parent(repos_root):
    """
    Ensure repo parent folder is detected properly.
    """
    assert Repository().parent == repos_root


def test_repr(current_repo_root):
    """
    Ensure __repr__ behaves correctly.
    """
    assert repr(Repository()) == "<tk_toolchain.repo.Repository for {0}>".format(
        current_repo_root
    )


def test_repo_name(tk_engine_root):
    """
    Ensure repo name is detected correctly.
    """
    # Do not use the current repo here for the test, because Azure
    # clones in a folder with a random string.
    assert Repository(tk_engine_root).name == "tk-maya"


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
    assert repo.is_shotgun_component()
    assert repo.is_toolkit_component() == (
        is_tk_core or is_framework or is_engine or is_config or is_app
    )

    if is_python_api or is_tk_toolchain:
        assert repo.is_toolkit_component() is False
    else:
        assert repo.is_toolkit_component()


def test_is_tk_core(tk_core_root):
    """
    Ensure tk-core repo is detected as such.
    """
    _test_component(Repository(tk_core_root), is_tk_core=True)


def test_is_framework(tk_framework_root):
    """
    Ensure framework repo is detected as such.
    """
    _test_component(Repository(tk_framework_root), is_framework=True)


def test_is_engine(tk_engine_root):
    """
    Ensure engine repo is detected as such.
    """
    _test_component(Repository(tk_engine_root), is_engine=True)


def test_is_app(tk_app_root):
    """
    Ensure app repo is detected as such.
    """
    _test_component(Repository(tk_app_root), is_app=True)


def test_is_config(tk_config_root):
    """
    Ensure config repo is detected as such.
    """
    _test_component(Repository(tk_config_root), is_config=True)


def test_is_python_api(python_api_root):
    """
    Ensure python-api repo is detected as such.
    """
    _test_component(Repository(python_api_root), is_python_api=True)


@pytest.mark.parametrize(
    "repo_name",
    [
        "tk-config-basic",
        "tk-core",
        "tk-multi-publish2",
        "tk-maya",
        "tk-framework-shotgunutils",
        "python-api",
    ],
)
def test_ensure_test_repositories_exists(repo_name):
    """
    Ensure all repositories required for the test to pass are present on the
    computer.
    """
    repo_path = os.path.join(Repository().parent, repo_name)
    assert os.path.exists(repo_path), (
        "Repository %s does not exist. Clone the master branch from Github for the test suite to pass."
        % repo_path
    )
