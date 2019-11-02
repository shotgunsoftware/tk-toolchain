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

from tk_toolchain.cmd_line_tools import tk_docs_preview

CURRENT_REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
REPOS_ROOT = os.path.dirname(CURRENT_REPO_ROOT)

TK_CORE_ROOT = os.path.join(REPOS_ROOT, "tk-core")
TK_FRAMEWORK_ROOT = os.path.join(REPOS_ROOT, "tk-framework-shotgunutils")
PYTHON_API_ROOT = os.path.join(REPOS_ROOT, "python-api")


# Note: These tests are likely to introduce side effects because they monkey patch toolkit.
# For now we're running the in-process because it makes coverage more easier to retrieve


def test_generate_doc_without_any_parameters():
    """
    Make sure we can generate documentation from inside a repo without any arguments.
    """
    cwd = os.getcwd()
    os.chdir(os.path.join(REPOS_ROOT, "tk-core"))
    try:
        assert tk_docs_preview.main(["tk_docs_preview", "--build-only"]) == 0
    finally:
        os.chdir(cwd)


# Disabling this test as the doc for the Python API is currently broken!
def _test_generate_doc_with_python_api():
    """
    Make sure we can generate documentation for a non toolkit repo.
    """
    assert (
        tk_docs_preview.main(
            ["tk_docs_preview", "--build-only", "--bundle={0}".format(PYTHON_API_ROOT)]
        )
        == 0
    )


def test_generate_doc_with_tk_core():
    """
    Make sure we can generate documentation for tk-core
    """
    assert (
        tk_docs_preview.main(
            ["tk_docs_preview", "--build-only", "--bundle={0}".format(TK_CORE_ROOT)]
        )
        == 0
    )


def test_generate_doc_with_tk_framework_shotgunutils():
    """
    Make sure we can generate documentation for a bundle that uses tk-core
    """
    assert (
        tk_docs_preview.main(
            [
                "tk_docs_preview",
                "--build-only",
                "--bundle={0}".format(TK_FRAMEWORK_ROOT),
                "--core={0}".format(TK_CORE_ROOT),
            ]
        )
        == 0
    )
