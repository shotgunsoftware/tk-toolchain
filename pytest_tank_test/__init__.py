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

from __future__ import print_function

from tk_toolchain.repo import Repository
from tk_toolchain import util
from tk_toolchain.tk_testengine import get_test_engine_environment
from .tk_fixtures import (  # noqa
    tk_test_project,
    tk_test_shotgun,
    tk_test_current_user,
    tk_test_entities,
)
from ruamel.yaml import YAML

import os
import sys


def _update_sys_path(reason, path):
    """
    Adds a path to sys.paths if it is missing.
    """
    if os.path.exists(path):
        print("{0}: {1}".format(reason, path))
        sys.path.insert(0, path)


def _initialize_logging():
    """
    Sets up a log file for the unit tests and optionally logs everything to the
    console.
    """
    import tank

    tank.LogManager().initialize_base_file_handler("tk-test")
    tank.LogManager().initialize_custom_handler()
    print("Logs for this test run can be found at", tank.LogManager().log_file)


def pytest_configure(config):
    """
    Configures the environment so that tests can
    - import sgtk
    - import tank_test
    - find the repository root via SHOTGUN_CURRENT_REPO_ROOT
    - find the test engine via SHOTGUN_TEST_ENGINE
    - write to a Toolkit log file
    """

    cur_dir = os.path.abspath(os.curdir)

    # The path to the current repo root
    try:
        repo = Repository(cur_dir)
    except RuntimeError:
        valid_repo = False
    else:
        # Make sure we're in a toolkit component
        valid_repo = repo.is_shotgun_component()
    # If we were unable to construct a Repository object, or if we're not in a
    # shotgun component repo, bail.
    if valid_repo is False:
        print(
            "%s does not appear to be inside Shotgun repository. Skipping initialization of 'pytest_tank_test.'"
            % cur_dir
        )
        return

    # Print Python interpreter location so that on CI we know where the
    # interpreter is on disk. This can be helpful when trying to launch
    # a specific Python on CI.
    print("Python running from {0}".format(sys.executable))

    print("Repository found at {0}".format(repo.root))

    # tk-toolchain assumes that the other repositories are clone alongside
    # the current one with their real name. However, for the current repo,
    # we can't make such an assumption.
    #
    # On Azure Pipeline for example, when testing an app we will clone alongside
    # the repo all the dependencies, including tk-core, which means we'll have
    # control over the folder names used for the repositories. However, when
    # Azure runs a build for tk-core, it will clone it inside a folder not named
    # after the repo. As such, we have to use whatever name we're given for
    # tk-core.
    if repo.is_tk_core() is False:
        tk_core_repo_root = os.path.join(repo.parent, "tk-core")
        if not os.path.exists(tk_core_repo_root):
            raise RuntimeError(
                "tk-core, which is a dependency of {}, should be cloned before the tests are executed:\n"
                "pushd .. && git clone git@github.com:shotgunsoftware/tk-core.git && popd".format(
                    repo.name
                )
            )
    else:
        tk_core_repo_root = repo.root

    # Adds the tk-core/python folder to the PYTHONPATH so we can import Toolkit
    _update_sys_path("Adding Toolkit folder", os.path.join(tk_core_repo_root, "python"))

    # Now that Toolkit has been added to the PYTHONPATH, we can set up logging.
    _initialize_logging()

    # Adds the tk-core/tests/python folder to the PYTHONPATH so TanTestBase
    # is available.
    _update_sys_path(
        "Adding Toolkit test framework",
        os.path.join(tk_core_repo_root, "tests", "python"),
    )

    # Add the <current-repo>/tests/python folder to the PYTHONPATH so custom
    # python modules from it can be used in the tests.
    # If we're running tests inside tk-core, we shouldn't add it as tk-toolchain
    # includes everything we need.
    if repo.is_tk_core() is False:
        _update_sys_path(
            "Adding repository tests/python folder",
            os.path.join(repo.root, "tests", "python"),
        )

    util.merge_into_environment_variables(repo.get_roots_environment_variables())
    util.merge_into_environment_variables(get_test_engine_environment())

    print("Fixtures found at", os.path.join(repo.root, "tests", "fixtures"))
    # Note: This won't be documented (or renamed) as we're not super comfortable
    # supporting TankTestBase at the moment for clients to write tests with.
    os.environ["TK_TEST_FIXTURES"] = os.path.join(repo.root, "tests", "fixtures")

    _ensure_dependencies(repo)


def _ensure_dependencies(repo):
    """
    Ensure all dependencies to run the tests are present.

    info.yml is not sufficient, because it doesn't enumerate the dependencies
    needed to run the tests. Therefore, we're going to look at Azure-Pipelines,
    which has the list of repositories to clone in order to run the tests.
    """
    # azure-pipelines.yml enumerates the repo necessary for the tests to run
    # so let's use that.
    azurepipelines_yml_path = os.path.join(repo.root, "azure-pipelines.yml")
    if not os.path.exists(azurepipelines_yml_path):
        return

    # Read azure-pipelines.yml so we can search for test dependencies.
    with open(azurepipelines_yml_path, "rt") as fh:
        yaml = YAML()
        azurepipelines_yml = yaml.load(fh)

    # Here's an example of an azure-pipelines.yml file.
    # jobs:
    # - template: build-pipeline.yml@templates
    #   parameters:
    #     additional_repositories:
    #     - name: tk-framework-shotgunutils
    #     - name: tk-multi-publish2
    for job in azurepipelines_yml.get("jobs", []):
        # There can be multiple jobs. Look for the one which has the additional_repositories
        # parameter. That's the one that enumerates all Toolkit repositories required for
        # the tests.
        additional_repositories = job.get("parameters", {}).get(
            "additional_repositories", []
        )
        # For each of the additional repositories...
        for additional_repository in additional_repositories:
            # ... look on disk if the repository is cloned ...
            repo_location = os.path.join(repo.parent, additional_repository["name"])
            if not os.path.exists(repo_location):
                # ... Dependency missing. Print helpful message.
                raise RuntimeError(
                    "{0}, which is a dependency of {1}, should be cloned before the tests are executed:\n"
                    "pushd .. && git clone git@github.com:shotgunsoftware/{0}.git && popd".format(
                        additional_repository["name"], repo.name
                    )
                )


def pytest_ignore_collect(path, config):
    """
    Ignore unit tests for third parties found inside tk-core and any Python
    source file inside tests/fixtures.
    """
    return os.path.join("tests", "python", "third_party") in str(path) or os.path.join(
        "tests", "fixtures"
    ) in str(path)
