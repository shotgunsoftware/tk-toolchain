# Copyright (c) 2018 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.


import os
import traceback


def get_caller_folder():
    """
    Returns the first caller of a method inside this module. This
    method needs to be called by a method called build_resources or
    build_ui.
    """

    # -1 is this function
    # -2 is build_resources or build_ui
    # -3 is the build_resources.py script.
    return os.path.dirname(traceback.extract_stack()[-3][0])
