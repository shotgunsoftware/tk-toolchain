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

from tk_toolchain.repo import Repository
from tk_toolchain.tk_testengine import get_test_engine_enviroment


def progress_callback(value, message):
    """
    Called by the ToolkitManager to report progress to the user.

    :param int value: Value between 0 to 1 indicating progress.
    :param str message:
    """
    print("[%s] %s" % (value, message))


def _start_engine(repo):
    """
    Bootstraps Toolkit and uses the app in the current repo.

    :param tk_toolchain.repo.Repository: Repository for the current folder.

    :returns: The tk-shell engine instance.
    """
    import sgtk

    # Initialize logging to disk and on screen.
    sgtk.LogManager().initialize_base_file_handler(
        "tk-run-app-{0}.log".format(repo.name)
    )
    sgtk.LogManager().initialize_custom_handler()

    # The config assumes that the frameworks and shell engine are located relative
    # to the SHOTGUN_REPOS_ROOT, which is in the parent folder of this repo.
    os.environ["SHOTGUN_REPOS_ROOT"] = repo.parent

    # The config assumes the app is in the current repo.
    os.environ["SHOTGUN_CURRENT_REPO_ROOT"] = repo.root

    os.environ.update(get_test_engine_enviroment())
    # import pdb;pdb.set_trace()
    # Standard Toolkit bootstrap code.
    sa = sgtk.authentication.ShotgunAuthenticator()
    user = sa.get_user()
    mgr = sgtk.bootstrap.ToolkitManager(user)
    mgr.progress_callback = progress_callback
    # Do not look in Shotgun for a config to load, we absolutely want to
    # use the config referenced by the base_configuration.
    mgr.do_shotgun_config_lookup = False
    mgr.base_configuration = "sgtk:descriptor:path?path={0}/config".format(
        os.path.dirname(__file__)
    )
    # Find the first non-template project and use it.
    # In the future we could have command-line arguments that allow to specify that.
    engine = mgr.bootstrap_engine(
        "tk-testengine",
        user.create_sg_connection().find_one("Project", [["is_template", "is", False]]),
    )
    return engine


####################################################################################
# script entry point
def main():
    """
    This will launch all the Toolkit applications and panels registered at app init
    and wait until all of them have been closed.
    """

    # Find the current repo and add Toolkit to the PYTHONPATH so we ca import it.
    repo = Repository(os.getcwd())
    tk_core = os.path.join(repo.parent, "tk-core", "python")
    sys.path.insert(0, tk_core)

    # We need to initialize QApplication before the engine is loaded or some
    # apps won't register themselves.
    try:
        from PySide import QtGui
    except ImportError:
        from PySide2 import QtWidgets

        app = QtWidgets.QApplication([])
    else:
        app = QtGui.QApplication([])

    engine = _start_engine(repo)

    print("Available commands:")
    pprint(engine.commands)

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
    for name, info in engine.commands.items():
        # We'll iterate on every app and when we find the app instance that is inside the
        # configuration, we'll launch it.
        if "app" not in info["properties"]:
            # Certain commands are not coming from apps, so skip those for now.
            continue
        if info["properties"]["app"].instance_name == "tk-multi-run-this-app":
            info["callback"]()

    # Loops until all dialogs are closed.
    app.exec_()

    sys.exit(0)
