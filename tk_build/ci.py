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


def is_in_ci_environment():
    """
    Returns ``True`` if in a CI environment, ``False`` otherwise.
    """
    return "CI" in os.environ


def is_travis():
    return os.environ.get("CI", "").lower() == "travis"


def get_cloned_folder_root():
    """
    Returns the folder into which the tested repository has been cloned it.
    """
    if "TRAVIS" in os.environ:
        return os.environ["TRAVIS_BUILD_DIR"]
    elif "APPVEYOR" in os.environ:
        return os.environ["APPVEYOR_BUILD_FOLDER"]
    else:
        raise RuntimeError("This CI service is not supported!")
