# -*- coding: utf-8 -*-
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


def expand_path(path):
    """
    Expand a path's environment variables and ``~``.

    :param str path: Path to expand.

    :returns: The expanded path.
    """
    # TODO: What is an env var contains an env var?
    return os.path.expanduser(os.path.expandvars(path))


def merge_into_environment_variables(env):
    """
    Merge the passed in environment variables into the real
    environment.

    If an environment variable is already defined, the original
    value will remain.
    """
    for name, value in env.items():
        os.environ.setdefault(name, value)
