# -*- coding: utf-8 -*-


import os
import sys


def _is_repo_root(path):
    files = os.listdir(path)
    for repo in [".git", ".svn", ".hg"]:
        if repo in files:
            return True
    return False


def _find_repo_root(path):
    while path and not _is_repo_root(path):
        path = os.path.dirname(path)

    return path


def _update_sys_path(reason, path):
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

    repo_root = _find_repo_root(cur_dir)

    if os.path.basename(repo_root).lower() != "tk-core":
        _update_sys_path(
            "Adding repository tests/python folder", os.path.join(repo_root, "tests", "python")
        )

    tk_core_repo_root = os.path.join(os.path.dirname(repo_root), "tk-core")

    _update_sys_path(
        "Adding Toolkit folder", os.path.join(tk_core_repo_root, "python")
    )

    _update_sys_path(
        "Adding Toolkit test framework",
        os.path.join(tk_core_repo_root, "tests", "python")
    )

    _update_sys_path(
        "Adding Toolkit test third-parties",
        os.path.join(os.path.dirname(repo_root), "tk-core", "tests", "python", "third_party")
    )

    os.environ["TK_TEST_FIXTURES"] = os.path.join(repo_root, "tests", "fixtures")


# Ignore unit tests found inside tk-core.
def pytest_ignore_collect(path, config):
    return os.path.join("tests", "python", "third_party") in str(path)
