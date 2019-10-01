#!/usr/bin/env python
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

####################################################################################
# imports and general setup

import os
import logging
import webbrowser
import optparse
import sys

from tk_toolchain.repo import Repository


def progress_callback(value, message):
    print("[%s] %s" % (value, message))


####################################################################################
# script entry point
def main():

    repo = Repository(os.getcwd())
    tk_core = os.path.join(repo.name, "tk-core", "python")
    sys.path.insert(0, tk_core)

    import sgtk

    sgtk.LogManager().initialize_base_file_handler(
        "tk-run-app-{0}.log".format(repo.name)
    )

    os.environ["SHOTGUN_REPOS_ROOT"] = repo.parent
    os.environ["SHOTGUN_CURRENT_REPO_ROOT"] = repo.root

    mgr = sgtk.bootstrap.ToolkitManager()
    mgr.progress_callback = progress_callback
    mgr.do_shotgun_config_lookup = False
    mgr.base_configuration = "sgtk:descriptor:path?path={0}/config".format(
        os.path.dirname(__file__)
    )
    engine = mgr.bootstrap_engine("tk-shell", None)

    print(engine.commands)

    sys.exit(0)
