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
from tk_toolchain.testing import create_unique_name


def test_with_env_var():
    """
    Ensure the env var is added to the name
    """
    os.environ["SHOTGUN_TEST_ENTITY_SUFFIX"] = "Potatoe"
    project_name = create_unique_name("Test-")
    assert project_name == "Test-Potatoe"


def test_without_env_var():
    """
    Ensure we are only getting the name
    """
    if "SHOTGUN_TEST_ENTITY_SUFFIX" in os.environ:
        del os.environ["SHOTGUN_TEST_ENTITY_SUFFIX"]
    project_name = create_unique_name("Test")
    assert project_name == "Test"
