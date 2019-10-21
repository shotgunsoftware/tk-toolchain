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


def get_test_engine_enviroment():
    """
    Return the environment variables necessary to run the test engine.

    :returns: Dictionary of environment variables necessary to run
        the test engine.
    """
    return {"SHOTGUN_TEST_ENGINE": os.path.dirname(__file__)}
