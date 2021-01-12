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


def create_unique_name(name):
    """
    Create a project unique name by passing environment.
    """
    if "SHOTGUN_TEST_ENTITY_SUFFIX" in os.environ:
        project_name = name + os.environ["SHOTGUN_TEST_ENTITY_SUFFIX"]
    else:
        project_name = name

    return project_name
