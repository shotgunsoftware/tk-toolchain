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
import tempfile

from tk_toolchain.cmd_line_tools import tk_docs_preview

CURRENT_REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
REPOS_ROOT = os.path.dirname(CURRENT_REPO_ROOT)

TK_CONFIG_ROOT = os.path.join(REPOS_ROOT, "tk-config-basic")
TK_CORE_ROOT = os.path.join(REPOS_ROOT, "tk-core")
TK_FRAMEWORK_ROOT = os.path.join(REPOS_ROOT, "tk-framework-shotgunutils")
PYTHON_API_ROOT = os.path.join(REPOS_ROOT, "python-api")


# Note: These tests are likely to introduce side effects because they monkey
# patch toolkit. For now we're running them in-process because it makes
# coverage easier to retrieve


def test_without_any_parameters():
    """
    Make sure we can generate documentation from inside a repository
    without any arguments.
    """
    cwd = os.getcwd()
    # Switch current folder to the framework so we can test both the core and
    # framework detection code path.
    os.chdir(TK_FRAMEWORK_ROOT)
    try:
        assert tk_docs_preview.main(["tk_docs_preview", "--build-only"]) == 0
    finally:
        os.chdir(cwd)


# Disabling this test as the doc for the Python API is currently broken!
def _test_with_python_api():
    """
    Make sure we can generate documentation for a non toolkit repo.
    """
    assert (
        tk_docs_preview.main(
            ["tk_docs_preview", "--build-only", "--bundle={}".format(PYTHON_API_ROOT)]
        )
        == 0
    )


def test_with_tk_core():
    """
    Make sure we can generate documentation for tk-core
    """
    assert (
        tk_docs_preview.main(
            ["tk_docs_preview", "--build-only", "--bundle={}".format(TK_CORE_ROOT)]
        )
        == 0
    )


def test_with_tk_framework_shotgunutils():
    """
    Make sure we can generate documentation for a bundle that uses tk-core
    """
    assert (
        tk_docs_preview.main(
            [
                "tk_docs_preview",
                "--build-only",
                "--bundle={}".format(TK_FRAMEWORK_ROOT),
                "--core={}".format(TK_CORE_ROOT),
            ]
        )
        == 0
    )


def test_with_repo_without_doc():
    """
    Make sure the doc generation tool exits gracefully when there is no docs folder.
    """
    assert (
        tk_docs_preview.main(
            [
                "tk_docs_preview",
                "--build-only",
                "--bundle={}".format(TK_CONFIG_ROOT),
                "--core={}".format(TK_CORE_ROOT),
            ]
        )
        == 0
    )


def test_with_unknown_folder():
    """
    Make sure the doc generation tool exits gracefully when we're not in a Toolkit
    repo
    """
    assert (
        tk_docs_preview.main(
            [
                "tk_docs_preview",
                "--build-only",
                "--bundle={}".format(tempfile.gettempdir()),
                "--core={}".format(TK_CORE_ROOT),
            ]
        )
        == 0
    )
