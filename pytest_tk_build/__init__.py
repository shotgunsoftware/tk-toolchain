# -*- coding: utf-8 -*-

from tk_build import ci, qt, repo
import os
import inspect
import sys


def _update_sys_path(reason, path):
    if os.path.exists(path):
        print("{0}: {1}".format(reason, path))
        sys.path.insert(0, path)


def _initialize_logging(config):
    """
    Sets up a log file for the unit tests and optionally logs everything to the
    console.
    """
    import tank
    tank.LogManager().initialize_base_file_handler("run_tests")

    tank.LogManager().initialize_custom_handler()

    tank.LogManager().global_debug = True


def pytest_configure(config):

    # FIXME: Should look at where pytest is picking tests from?
    cur_dir = os.path.abspath(os.curdir)

    repo_root = repo.find_repo_root(cur_dir)

    # If we're not in the tk-core repo, we should add the current repo's python
    # folder since it may have custom tools.
    if os.path.basename(repo_root).lower() != "tk-core":
        _update_sys_path(
            "Adding repository tests/python folder",
            os.path.join(repo_root, "tests", "python")
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

    os.environ["TK_TEST_FIXTURES"] = os.path.join(
        repo_root, "tests", "fixtures"
    )

    # Extra work needs to be done for CI environments. We need to make sure Qt
    # is available if it was specified.
    if ci.is_in_ci_environment() and qt.is_qt_required():
        os.environ.update(qt.get_runtime_env_vars())

    os.environ["SHOTGUN_TEST_ENGINE"] = os.path.join(
        os.path.dirname(inspect.getsourcefile(pytest_configure)),
        "tk-testengine"
    )


# Ignore unit tests for third parties found inside tk-core.
def pytest_ignore_collect(path, config):
    return (
        os.path.join("tests", "python", "third_party") in str(path) or
        os.path.join("tests", "fixtures") in str(path)
    )
