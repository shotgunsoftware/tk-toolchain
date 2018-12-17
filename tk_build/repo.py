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


def _is_repo_root(path):
    files = os.listdir(path)
    for repo in [".git", ".svn", ".hg"]:
        if repo in files:
            return True
    return False


def find_repo_root(path):
    """
    Finds the root of the repo given a given path to a file inside it.

    :param str path: Path to a file inside the repo.

    :returns: Path to the repo.
    """
    while path and not _is_repo_root(path):
        path = os.path.dirname(path)

    # TODO: Add check for when there is no repo root!
    return path
