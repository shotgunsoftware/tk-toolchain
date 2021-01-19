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

import pytest
import os


def create_unique_name(name):
    """
    Create a unique name.

    When ``SHOTGUN_TEST_ENTITY_SUFFIX`` is set, the suffix is added to the name. This can be useful
    in a CI environment where multiple resources can be created on a server and each need a unique
    name.

    It is the responsibility of the CI environment to set ``SHOTGUN_TEST_ENTITY_SUFFIX`` for this method
    to work. If the environment variable is not set, the name is returned as is.

    :param str name: Name that needs to be made unique.

    :returns: The name with a suffix is one was specified by the environment variable.
    """
    if "SHOTGUN_TEST_ENTITY_SUFFIX" in os.environ:
        unique_name = name + " - " + os.environ["SHOTGUN_TEST_ENTITY_SUFFIX"]
    else:
        unique_name = name

    return unique_name
