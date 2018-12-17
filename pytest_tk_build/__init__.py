# -*- coding: utf-8 -*-

from tk_build import find_repo_root
import os
import sys


def _update_sys_path(reason, path):
    if os.path.exists(path):
        print("{0}: {1}".format(reason, path))
        sys.path.insert(0, path)


def _initialize_logging(config):
    """
    Sets up a log file for the unit tests and optionally logs everything to the console.
    """
    import tank
    tank.LogManager().initialize_base_file_handler("run_tests")

    tank.LogManager().initialize_custom_handler()

    tank.LogManager().global_debug = True


def pytest_configure(config):
    # FIXME: Should look at where pytest is picking tests from?
    cur_dir = os.path.abspath(os.curdir)

    repo_root = find_repo_root(cur_dir)

    # If we're not in the tk-core repo, we should add the current repo's python folder since it may
    # have custom tools.
    if os.path.basename(repo_root).lower() != "tk-core":
        _update_sys_path(
            "Adding repository tests/python folder", os.path.join(repo_root, "tests", "python")
        )

    repos_root = os.path.dirname(repo_root)
    # FIME: Named this way to please the publisher tests, but should probably
    # be named SHOTGUN_REPOS_ROOT
    os.environ["SHOTGUN_EXTERNAL_REPOS_ROOT"] = repos_root

    tk_core_repo_root = os.path.join(repos_root, "tk-core")

    _update_sys_path(
        "Adding Toolkit folder", os.path.join(tk_core_repo_root, "python")
    )

    _update_sys_path(
        "Adding Toolkit test framework",
        os.path.join(tk_core_repo_root, "tests", "python")
    )

    os.environ["TK_TEST_FIXTURES"] = os.path.join(repo_root, "tests", "fixtures")


# Ignore unit tests found inside tk-core.
def pytest_ignore_collect(path, config):
    return (
        os.path.join("tests", "python", "third_party") in str(path) or
        os.path.join("tests", "fixtures") in str(path)
    )