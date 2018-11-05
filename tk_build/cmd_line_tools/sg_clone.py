#!/usr/bin/env python

# Copyright (c) 2018 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Shotgun Build Repository Clone Tool

Usage: sg_clone.py <repo-name>...

To make cloning easier, you can type in a single word as the repository name. In
this case, the repository will be assumed to be under
"https://github.com/shotgunsoftware".

If you type two words separated by a forward slash ("/"), then the repository
will be assumed to be under "https://github.com".

If your repository is under another Git host, like Gitlab, you can set
the SHOTGUN_CLONE_HOST environment variable and point it to the URL of the
Git host. Note that the Git host doesn't have to be a remote server and could
actually be a local repository.

By default, the command will clone the repository under the current folder. If
the script is run in a CI environment, the repository will be cloned alongside
the repository that was cloned by the CI service.
"""

from __future__ import print_function

import os

from docopt import docopt

from tk_build import ci, git


def get_full_name(repo_name):
    """
    Converts the repo name into a fully qualified repo name if it wasn't.

    If ``repo_name`` is a single word, https://github.com/shotgunsoftware is prefixed.
    If ``repo_name`` is a two words seperated by "/", word, https://github.com/is prefixed.
    Otherwise, returns the repo name as is.

    :returns: The fully qualified repo name.
    """
    if "/" not in repo_name:
        return "https://github.com/shotgunsoftware/%s" % repo_name
    elif repo_name.count("/") == 1:
        return "https://github.com/%s" % repo_name
    else:
        return repo_name


def sg_clone():

    arguments = docopt(__doc__, version='Shotgun Build Repository Clone Tool 0.1')

    if ci.is_in_ci_environment():
        execution_folder = ci.get_cloned_folder_root()
    else:
        execution_folder = os.curdir

    print("Git commands will be executed in '%s'..." % execution_folder)

    for repo_name in arguments["<repo-name>"]:
        repo_name = get_full_name(repo_name)
        print("Shallow cloning of repository %s" % repo_name)
        git.clone_repo(repo_name, execution_folder, 1, "master")

    return 0


if __name__ == "__main__":
    sg_clone()
