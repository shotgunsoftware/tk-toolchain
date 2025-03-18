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

import argparse
import os
import sys
from pprint import pprint

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


def _start_engine(repo, entity_type, entity_id, config):
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
        config if config else get_config_location()
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


def _is_app_command(info):
    """
    Checks if an app is an application command.

    :returns: ``True`` if this is an app command, ``False`` otherwise.
    """
    # Application commands always have properties.
    if "app" not in info["properties"]:
        # Certain commands are not coming from apps, so skip those for now.
        return False
    # Make sure that the application command is from the app in the current repo.
    return info["properties"]["app"].instance_name == "tk-multi-run-this-app"


def _get_available_commands(engine):
    """
    Gets all available commands, long and short names, prints them on screen
    and returns them.

    :param engine: The Toolkit engine for which we desire to extract commands.

    :returns: ``list`` of command ``str`` names.
    """
    long_command_names = sorted(
        name for name, info in engine.commands.items() if _is_app_command(info)
    )

    # Add the list of short commands, sorted.
    possible_commands = long_command_names + sorted(
        info["properties"]["short_name"]
        for info in engine.commands.values()
        if _is_app_command(info) and "short_name" in info["properties"]
    )

    print("Available application commands (long and short versions):")
    pprint(possible_commands)

    return possible_commands, long_command_names


def _validate_requested_commands(commands, available_commands, long_command_names):
    """
    Gets the list of commands the user wishes to execute, prints them
    and returns them.

    :param commands: List of commands the user typed in.
    :param available_commands: List of commands, short and long, available.
    :param engine: The Toolkit engine for which we desire to validate commands.

    :returns: ``list`` of command ``str`` names.
    """
    for command in commands:
        if command not in available_commands:
            raise SystemExit("Command '%s' does not exist." % command)

    print("The following commands will be run:")
    if commands:
        pprint(sorted(commands))
        return commands
    else:
        # Only print the long command names for clarity. Not every app has a short
        # command name so trying to print only these could cause issues anyway.
        print(sorted(long_command_names))
        return sorted(long_command_names)


####################################################################################
# script entry point
def main(arguments=None):
    """
    This will launch all the Toolkit applications and panels registered at app init
    and wait until all of them have been closed.
    """

    parser = argparse.ArgumentParser(
        description="""
            Toolkit Application Runner

            Launch a Toolkit application from the command line by running this
            tool in any Toolkit repository.
        """,
    )

    parser.add_argument(
        "--context-entity-type",
        "-e",
        help="Specifies the type of the entity of the context",
    )

    parser.add_argument(
        "--context-entity-id",
        "-i",
        help="Specifies the id of the entity of the context",
    )

    parser.add_argument(
        "--location",
        help="""
            Specifies the location where the Toolkit application is.
            If missing, the tk-run-app assumes it is run from inside
            the repository and launch the application at the root of
            it.
        """,
    )

    parser.add_argument(
        "--commands",
        help="""
            Comma-separated list of commands to run. These can be long
            or short Toolkit command names. If missing, tk-run-app
            assumes all commands should be run.
        """,
    )

    parser.add_argument(
        "--config",
        "-c",
        help="Specifies the location of the Toolkit config folder to use",
    )

    args = parser.parse_args(args=arguments)

    # Check to see if a Toolkit config location was passed and resolve any
    # environment variables in the path.
    config = util.expand_path(args.config) if args.config else None

    if config and not os.path.exists(config):
        print("This config location does not exist. %s" % config)
        return 1

    # Find the current repo and add Toolkit to the PYTHONPATH so we ca import it.
    repo = Repository(util.expand_path(args.location or os.getcwd()))
    tk_core = os.path.join(repo.parent, "tk-core", "python")
    sys.path.insert(0, tk_core)

    if args.commands:
        commands_to_run = [
            command.strip() for command in (args.commands or "").split(",")
        ]
    else:
        commands_to_run = []

    if repo.is_app() is False:
        print("This location does not have a Toolkit application.")
        return 1

    engine = _start_engine(
        repo,
        (
            args.context_entity_type
            if args.context_entity_type is not None
            else "Project"
        ),
        (int(args.context_entity_id) if args.context_entity_id is not None else None),
        config,
    )

    available_commands, long_command_names = _get_available_commands(engine)
    _validate_requested_commands(
        commands_to_run, available_commands, long_command_names
    )

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
        if _is_app_command(info) is False:
            continue
        if "short_name" in info["properties"]:
            short_name = info["properties"]["short_name"]
        else:
            short_name = None
        # If no commands were specified, launch every app app!
        # If the long name of the command matched one of the commands to run, launch it!
        # if the short name of the command matched one of the commands to run, launch it!
        if (
            not commands_to_run
            or name in commands_to_run
            or short_name in commands_to_run
        ):
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
