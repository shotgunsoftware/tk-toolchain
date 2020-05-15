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

"""
Toolkit Application Runner

Launch a Toolkit application from the command line by running this tool in any
Toolkit repository.

Usage:
    tk-run-app [--context-entity-type=<entity-type>] [--context-entity-id=<entity-id>] [--location=<location>]

Options:

    -e, --context-entity-type=<entity-type>
                       Specifies the type of the entity of the context.

    -i, --context-entity-id=<entity-id>
                       Specifies the id of the entity of the context.

    --location=<location>
                        Specifies the location where the Toolkit application is.
                        If missing, the tk-run-app assumes it is run from inside
                        the repository and launch the application at the root of
                        it.
"""

import os
import sys
from pprint import pprint

import docopt

from tk_toolchain.repo import Repository
from tk_toolchain import util, authentication
from tk_toolchain.tk_testengine import get_test_engine_environment


def get_config_location():
    """
    Return the location of the configuration tk-run-app uses.
    """
    return os.path.join(os.path.dirname(__file__), "config")


def _progress_callback(value, message):
    """
    Called by the ToolkitManager to report progress to the user.

    :param int value: Value between 0 to 1 indicating progress.
    :param str message:
    """
    print("[%s] %s" % (value, message))


def _start_engine(repo, entity_type, entity_id):
    """
    Bootstraps Toolkit and uses the app in the current repo.

    :param tk_toolchain.repo.Repository: Repository for the current folder.

    :returns: An engine instance.
    """
    import sgtk

    # Initialize logging to disk and on screen.
    sgtk.LogManager().initialize_base_file_handler("tk-run-app-{0}".format(repo.name))
    sgtk.LogManager().initialize_custom_handler()

    util.merge_into_environment_variables(repo.get_roots_environment_variables())
    util.merge_into_environment_variables(get_test_engine_environment())
    os.environ["SHOTGUN_TK_APP_LOCATION"] = repo.root

    # Standard Toolkit bootstrap code.
    user = authentication.get_toolkit_user()
    mgr = sgtk.bootstrap.ToolkitManager(user)
    mgr.progress_callback = _progress_callback
    # Do not look in Shotgun for a config to load, we absolutely want to
    # use the config referenced by the base_configuration.
    mgr.do_shotgun_config_lookup = False
    mgr.base_configuration = "sgtk:descriptor:path?path={0}".format(
        get_config_location()
    )

    if entity_type == "Project" and entity_id is None:
        context = user.create_sg_connection().find_one(
            "Project",
            [["is_template", "is", False]],
            order=[{"direction": "asc", "field_name": "id"}],
        )
    elif entity_id is None:
        context = user.create_sg_connection().find_one(
            entity_type, [], order=[{"direction": "asc", "field_name": "id"}]
        )
    elif entity_type and entity_id:
        context = user.create_sg_connection().find_one(
            entity_type, [["id", "is", entity_id]]
        )
    else:
        raise RuntimeError(
            "Bad context argument for {0}@{1}".format(entity_type, entity_id)
        )

    if context is None:
        raise RuntimeError(
            "Context enity {0} with id {1} could not be found.".format(
                entity_type, entity_id
            )
        )

    print("Python Version: {0}".format(sys.version))

    print("Launching test engine in context {0}".format(context))

    # Find the first non-template project and use it.
    # In the future we could have command-line arguments that allow to specify that.
    engine = mgr.bootstrap_engine("tk-testengine", context)
    return engine


####################################################################################
# script entry point
def main(arguments=None):
    """
    This will launch all the Toolkit applications and panels registered at app init
    and wait until all of them have been closed.
    """
    arguments = arguments or sys.argv[1:]

    # docopt does not care about the script name, so skip or we'll
    # get an error.
    options = docopt.docopt(__doc__, argv=arguments)

    # Find the current repo and add Toolkit to the PYTHONPATH so we ca import it.
    repo = Repository(util.expand_path(options["--location"] or os.getcwd()))
    tk_core = os.path.join(repo.parent, "tk-core", "python")
    sys.path.insert(0, tk_core)

    if repo.is_app() is False:
        print("This location does not have a Toolkit application.")
        return 1

    engine = _start_engine(
        repo,
        options["--context-entity-type"]
        if options["--context-entity-type"] is not None
        else "Project",
        int(options["--context-entity-id"])
        if options["--context-entity-id"] is not None
        else None,
    )

    print("Available commands:")
    pprint(sorted(engine.commands))

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
    app_launched = False
    for name, info in engine.commands.items():
        # We'll iterate on every app and when we find the app instance that is inside the
        # configuration, we'll launch it.
        if "app" not in info["properties"]:
            # Certain commands are not coming from apps, so skip those for now.
            continue
        if info["properties"]["app"].instance_name == "tk-multi-run-this-app":
            info["callback"]()
            app_launched = True

    if app_launched is False:
        print(
            "No commands were found. It is possible the application failed to initialize?"
        )
        return 1

    # Loops until all dialogs are closed.
    engine.q_app.exec_()

    return 0
