# -*- coding: utf-8 -*-
# Copyright (c) 2020 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import subprocess
import six

import pytest
from ruamel import yaml

from tk_toolchain.cmd_line_tools import tk_config_update

# We'll create a copy of the config for this test so we can
# run the tool on it without modifying it.
@pytest.fixture(scope="module")
def cloned_config(tk_config_root, tmpdir_factory):
    tmp_path = tmpdir_factory.mktemp("config")
    # cast LocalPath to str since Python 2 compatible methods manipulate strings
    tmp_path = str(tmp_path)
    subprocess.check_call(
        ["git", "clone", "--branch", "v1.3.0", tk_config_root, tmp_path]
    )
    return six.ensure_str(tmp_path)


@pytest.fixture
def test_config(cloned_config):
    """
    Provides a fresh and clean copy of the test config. Any modifications
    made to the configuration will be reverted after after the test.
    """
    try:
        yield cloned_config
    finally:
        subprocess.call(["git", "reset", "--hard"], cwd=cloned_config)


def test_enumerate_files(cloned_config):
    """
    Ensure the tool enumerates files correctly.

    If this test fails for you locally because new files were added or remove,
    simply update add the missing files and make sure the .travis.yml file clones the
    right tag.
    """
    files_found = [
        path.replace(cloned_config + "/", "")
        for path in tk_config_update.enumerate_yaml_files(cloned_config)
    ]
    assert set(files_found) == expected_config_files


def test_is_descriptor():
    assert tk_config_update.is_app_store_descriptor({"something": "something"}) is False
    assert (
        tk_config_update.is_app_store_descriptor(
            {"type": "shotgun", "name": "something", "version": "231"}
        )
        is False
    )
    assert (
        tk_config_update.is_app_store_descriptor(
            {"type": "app_store", "name": "something", "version": "231"}
        )
        is True
    )


@pytest.mark.parametrize(
    "modified_file,path_to_descriptor,bundle,expected_version",
    [
        (os.path.join("core", "core_api.yml"), ["location"], "tk-core", "v0.18.0"),
        (
            os.path.join(*"env/includes/common/frameworks.yml".split("/")),
            ["frameworks", "tk-framework-shotgunutils_v5.x.x", "location"],
            "tk-framework-shotgunutils",
            "v5.0.0",
        ),
        (
            os.path.join(*"env/includes/common/frameworks.yml".split("/")),
            ["frameworks", "tk-framework-shotgunutils_v4.x.x", "location"],
            "tk-framework-shotgunutils",
            "v4.0.0",
        ),
        (
            os.path.join(*"env/includes/common/apps.yml".split("/")),
            ["common.apps.tk-multi-publish2.location"],
            "tk-multi-publish2",
            "v10.0.0",
        ),
        (
            os.path.join(*"env/includes/common/engines.yml".split("/")),
            ["common.engines.tk-3dsmax.location"],
            "tk-3dsmax",
            "v11.0.0",
        ),
    ],
)
def test_update_config(
    cloned_config,
    test_config,
    modified_file,
    path_to_descriptor,
    bundle,
    expected_version,
):
    """
    Ensure the update updates the right file and puts the right content in it.
    """
    updated_files = list(
        tk_config_update.update_files(test_config, bundle, expected_version)
    )
    assert updated_files == [os.path.join(test_config, modified_file)]

    with open(os.path.join(cloned_config, modified_file), "rt") as fh:
        expected_cfg = yaml.load(fh, Loader=yaml.Loader)

    with open(os.path.join(test_config, modified_file), "rt") as fh:
        test_config = yaml.load(fh, Loader=yaml.Loader)

    value = expected_cfg
    for key in path_to_descriptor:
        value = value[key]

    value["version"] = expected_version

    assert expected_cfg == test_config


expected_config_files = set(
    [
        "env/includes/desktop2/site.yml",
        "env/includes/3dsmax/shot_step.yml",
        "env/includes/aftereffects/shot.yml",
        "env/includes/houdini/shot_step.yml",
        "azure-pipelines.yml",
        "env/includes/maya/project.yml",
        "env/includes/photoshopcc/shot.yml",
        "env/includes/maya/shot_step.yml",
        "env/includes/vred/apps.yml",
        "env/includes/3dsmax/site.yml",
        "env/includes/vred/project.yml",
        "core/core_api.yml",
        "env/includes/shell/project.yml",
        "env/includes/photoshopcc/asset_step.yml",
        "env/includes/flame/shot.yml",
        "env/asset_step.yml",
        "env/project.yml",
        "env/includes/alias/site.yml",
        "env/includes/maya/site.yml",
        "env/includes/maya/apps.yml",
        "env/site.yml",
        "env/includes/aftereffects/project.yml",
        "env/includes/photoshopcc/project.yml",
        "env/includes/aftereffects/apps.yml",
        "env/includes/photoshopcc/shot_step.yml",
        "env/includes/houdini/project.yml",
        "env/includes/flame/project.yml",
        "env/includes/common/apps.yml",
        "env/includes/houdini/asset_step.yml",
        "env/includes/houdini/shot.yml",
        "env/includes/shell/apps.yml",
        "env/includes/shotgun/all.yml",
        "env/includes/houdini/site.yml",
        "env/includes/desktop2/all.yml",
        "env/includes/alias/project.yml",
        "env/includes/maya/shot.yml",
        "env/publishedfile.yml",
        "env/includes/common/engines.yml",
        "env/shot.yml",
        "env/includes/desktop/site.yml",
        "env/includes/maya/asset_step.yml",
        "env/includes/3dsmax/project.yml",
        "env/includes/nuke/project.yml",
        "env/includes/3dsmax/asset_step.yml",
        "env/includes/flame/asset_step.yml",
        "env/includes/nuke/site.yml",
        "env/includes/nuke/asset_step.yml",
        "env/includes/nuke/apps.yml",
        "env/includes/3dsmax/shot.yml",
        "env/includes/common/settings/tk-multi-publish2.yml",
        "env/includes/alias/apps.yml",
        "env/includes/vred/site.yml",
        "env/includes/shell/shot.yml",
        "env/includes/common/frameworks.yml",
        "env/includes/photoshopcc/apps.yml",
        "env/includes/nuke/shot.yml",
        "env/shot_step.yml",
        "env/includes/shell/site.yml",
        "env/includes/aftereffects/asset_step.yml",
        "info.yml",
        "env/includes/houdini/apps.yml",
        "env/includes/shell/asset_step.yml",
        "env/includes/shell/shot_step.yml",
        "env/includes/aftereffects/shot_step.yml",
        "env/includes/flame/shot_step.yml",
        "env/includes/3dsmax/apps.yml",
        "core/roots.yml",
        "env/includes/desktop/project.yml",
        "env/includes/photoshopcc/site.yml",
        "env/includes/nuke/shot_step.yml",
        "env/includes/aftereffects/site.yml",
    ]
)
