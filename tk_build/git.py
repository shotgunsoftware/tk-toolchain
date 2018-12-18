# Copyright (c) 2018 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import subprocess
import sys
import os


def _can_hide_terminal():
    """
    Returns ``True`` if this version of Python can hide the terminal of a
    subprocess launched with the subprocess module, ``False`` otherwise.
    """
    try:
        # These values are not defined between Python 2.6.6 and 2.7.1
        # inclusively.
        subprocess.STARTF_USESHOWWINDOW
        subprocess.SW_HIDE
        return True
    except Exception:
        return False


def clone_repo(repo_path, execution_folder, depth=None, branch_name=None):
    """
    Clones a git repository.

    :param str repo_path: Path of the repository to clone.
    :param str execution_folder: Folder in which the git command will be run.
    :param optional(int) depth: If set, indicates how many commits to clone.
        Defaults to complete clone.
    :param optional(str) branch_name: if set, indicates which branch to
                                      checkout after the clone. Defaults to
                                      ``master``.
    """

    # Do not allow dialog to pop on Windows.
    startupinfo = None
    if sys.platform == "win32" and _can_hide_terminal():
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

    # Clone the repo with requite depth on the right branch.
    args = ["git", "-C", execution_folder, "clone", "-q", repo_path]
    if depth is not None:
        args.extend(["--depth", str(depth)])
    if branch_name is not None:
        args.extend(["--branch", branch_name])

    # Refuse to authenticate. This is supposed to work headless.
    environ = {}
    environ.update(os.environ)
    environ["GIT_TERMINAL_PROMPT"] = "0"

    # Clone the repo.
    subprocess.check_call(args, startupinfo=startupinfo)
