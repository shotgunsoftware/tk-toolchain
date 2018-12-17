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


def get_runtime_env_vars():
    """
    Returns ``True`` if in a CI environment, ``False`` otherwise.
    """
    return {"DISPLAY": ":99.0"}


def is_qt_required():
    return is_pyside1_required() or is_pyside2_required()


def is_pyside1_required():
    return get_qt_type() == "PySide"


def is_pyside2_required():
    return get_qt_type() == "PySide"


def get_qt_type():
    return os.environ.get("SG_QT_LIBRARY")

