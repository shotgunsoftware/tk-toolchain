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
from pprint import pprint
import itertools

from tk_toolchain.repo import Repository


def progress_callback(value, message):
    print("[%s] %s" % (value, message))


def _start_toolkit(repo):
    import sgtk

    sgtk.LogManager().initialize_base_file_handler(
        "tk-run-app-{0}.log".format(repo.name)
    )
    sgtk.LogManager().initialize_custom_handler()

    os.environ["SHOTGUN_REPOS_ROOT"] = repo.parent
    os.environ["SHOTGUN_CURRENT_REPO_ROOT"] = repo.root

    sa = sgtk.authentication.ShotgunAuthenticator()
    user = sa.get_user()
    mgr = sgtk.bootstrap.ToolkitManager(user)
    mgr.progress_callback = progress_callback
    mgr.do_shotgun_config_lookup = False
    mgr.base_configuration = "sgtk:descriptor:path?path={0}/config".format(
        os.path.dirname(__file__)
    )
    engine = mgr.bootstrap_engine(
        "tk-shell",
        user.create_sg_connection().find_one("Project", [["is_template", "is", False]]),
    )
    engine._initialize_dark_look_and_feel()
    return engine


####################################################################################
# script entry point
def main():

    repo = Repository(os.getcwd())
    tk_core = os.path.join(repo.parent, "tk-core", "python")
    sys.path.insert(0, tk_core)

    try:
        from PySide import QtGui
    except ImportError:
        from PySide2 import QtWidgets

        app = QtWidgets.QApplication([])
    else:
        app = QtGui.QApplication([])

    engine = _start_toolkit(repo)

    print("Available commands:")

    # Sample command:
    # 'Work Area Info...': {'callback': <function Engine.register_command.<locals>.callback_wrapper at 0x127affe18>,
    #                       'properties': {'app': <Sgtk App 0x11ec862b0: tk-multi-about, engine: <Sgtk Engine 0x11ce680f0: tk-shell, env: test>>,
    #                                      'description': 'Shows a breakdown of '
    #                                                     'your current environment '
    #                                                     'and configuration.',
    #                                      'icon': '/Users/boismej/gitlocal/tk-multi-about/icon_256.png',
    #                                      'prefix': None,
    #                                      'short_name': 'work_area_info',
    #                                      'type': 'context_menu'}}}
    for name, info in itertools.chain(engine.commands.items(), engine.panels.items()):
        if "app" not in info["properties"]:
            continue
        if info["properties"]["app"].instance_name == "tk-multi-run-this-app":
            info["callback"]()

    app.exec_()

    sys.exit(0)
