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


def test_generate_doc_with_python_api():
    """
    Make sure we can generate documentation for a non toolkit repo.
    """
    assert (
        tk_docs_preview.main(
            ["tk_docs_preview", "--build-only", "--bundle={}".format(PYTHON_API_ROOT)]
        )
        == 0
    )


def test_generate_doc_with_tk_core():
    """
    Make sure we can generate documentation for tk-core
    """
    assert (
        tk_docs_preview.main(
            ["tk_docs_preview", "--build-only", "--bundle={}".format(TK_CORE_ROOT)]
        )
        == 0
    )


def _test_generate_doc_with_tk_framework_shotgunutils():
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
