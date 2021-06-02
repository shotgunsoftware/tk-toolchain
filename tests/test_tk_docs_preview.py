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

from tk_toolchain.cmd_line_tools import tk_docs_generation


# Note: These tests are likely to introduce side effects because they monkey
# patch toolkit. For now we're running them in-process because it makes
# coverage easier to retrieve


def test_without_any_parameters(tk_framework_root):
    """
    Make sure we can generate documentation from inside a repository
    without any arguments.
    """
    cwd = os.getcwd()
    # Switch current folder to the framework so we can test both the core and
    # framework detection code path.
    os.chdir(tk_framework_root)
    try:
        assert tk_docs_generation.main(["tk_docs_preview", "--build-only"]) == 0
    finally:
        os.chdir(cwd)


def test_with_python_api(python_api_root):
    """
    Make sure we can generate documentation for a non toolkit repo.
    """

    assert (
        tk_docs_generation.main(
            ["tk_docs_preview", "--build-only", "--bundle={0}".format(python_api_root)]
        )
        == 0
    )


def test_with_tk_core(tk_core_root):
    """
    Make sure we can generate documentation for tk-core
    """
    assert (
        tk_docs_generation.main(
            ["tk_docs_preview", "--build-only", "--bundle={0}".format(tk_core_root)]
        )
        == 0
    )


def test_with_tk_framework_shotgunutils(tk_framework_root, tk_core_root):
    """
    Make sure we can generate documentation for a bundle that uses tk-core
    """
    assert (
        tk_docs_generation.main(
            [
                "tk_docs_preview",
                "--build-only",
                "--bundle={0}".format(tk_framework_root),
                "--core={0}".format(tk_core_root),
            ]
        )
        == 0
    )


def test_with_repo_without_doc(tk_config_root, tk_core_root):
    """
    Make sure the doc generation tool exits gracefully when there is no docs folder.
    """
    assert (
        tk_docs_generation.main(
            [
                "tk_docs_preview",
                "--build-only",
                "--bundle={}".format(tk_config_root),
                "--core={}".format(tk_core_root),
            ]
        )
        == 0
    )


def test_with_unknown_folder(tk_core_root):
    """
    Make sure the doc generation tool exits gracefully when we're not in a Toolkit
    repo
    """
    assert (
        tk_docs_generation.main(
            [
                "tk_docs_preview",
                "--build-only",
                "--bundle={}".format(tempfile.gettempdir()),
                "--core={}".format(tk_core_root),
            ]
        )
        == 0
    )
