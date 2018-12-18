
"""
Shotgun Build Repository Clone Tool

Usage: tk-ci-install.py [--dry-run]

This script will setup Qt and clone any repos needed to run tests on the CI
server.
"""

from __future__ import print_function

import subprocess
import os
import time
import yaml

from docopt import docopt

from tk_build import ci, qt, bundle
from tk_build.cmd_line_tools.tk_clone import tk_clone


def _install_qt(is_dry_run):

    qt_versions = {
        "PySide": "1.2.2",
        "PySide2": "5.12.0"
    }

    if ci.is_travis():

        qt_lib = qt.get_qt_type()
        qt_version = qt_versions[qt_lib]

        commands = []

        if qt.is_pyside1_required():
            # PySide does not come with Qt, so we'll have to install it.
            commands.append([
                "sudo",
                "apt-get",
                "install",
                "libqt4-dev"]
            )
            commands.append([
                "pip",
                "install",
                "{}=={}".format(qt_lib, qt_version),
                "--no-index",
                "--find-links",
                "https://parkin.github.io/python-wheelhouse/"
            ])
        else:
            commands.append([
                "pip",
                "install",
                "{}=={}".format(qt_lib, qt_version)
            ])

        if qt.is_pyside1_required():
            # PySide needs to be patched after install so we need to finish the install by the following
            commands.append([
                "python",
                os.path.expanduser(
                    os.path.expandvars(
                        "~/virtualenv/python${TRAVIS_PYTHON_VERSION}/bin/pyside_postinstall.py"
                    )
                ),
                "-install"
            ])

        # Now we need to start the X server...
        # Taken from:
        # https://github.com/colmap/colmap/commit/606d3cd09931d78a3272f99b5e7a2cb6894e243e
        commands.append([
            "sh",
            "-e",
            "/etc/init.d/xvfb",
            "start"
        ])

        # Ensures that everything worked.
        commands.append(["python", "-c", "import {}".format(qt.get_qt_type())])

        # update the environment variables to be able to run Qt
        env = {}
        env.update(os.environ)
        env.update(qt.get_runtime_env_vars())

        for cmd in commands:
            print("Running:", " ".join(cmd))
            if not is_dry_run:
                subprocess.check_call(cmd, env=env)

        if not is_dry_run:
            # Let the x server time to start.
            time.sleep(3)
    else:
        print("Qt will not be initialized for {}.".format(ci.get_ci_name()))


def _install_tk_core(is_dry_run):

    root_folder = ci.get_cloned_folder_root()
    if bundle.is_tk_build(root_folder) or bundle.is_tk_core(root_folder):
        print("Skipping tk-core cloning...")
    else:
        print("Cloning tk-core...")
        if not is_dry_run:
            tk_clone("tk-core", shallow=True)


def _install_toolkit_frameworks(is_dry_run):

    # Check if the info.yml exists.
    info_yml_path = os.path.join(ci.get_cloned_folder_root(), "info.yml")
    if not os.path.exists(info_yml_path):
        print("info.yml is missing.")
        return False

    # Read all the data.
    with open(info_yml_path, "rt") as fh:
        info = yaml.safe_load(fh)

    frameworks = info.get("frameworks", [])

    if not frameworks:
        print("No frameworks were found inside info.yml.")
        return

    # If there is a frameworks section, iterate on the items and clone the
    # repos.
    # FIXME: This assumes everything is under our org. This needs to be
    # expandable so clients can use their own org and repo location.
    # Maybe this can be a pluggy hook that allows to resolve a framework
    # url based on a name?
    # FIXME: This needs to work recursively.
    for fw in frameworks:
        print("Cloning {}...".format(fw["name"]))
        if not is_dry_run:
            tk_clone(fw["name"], shallow=True)


def main():

    arguments = docopt(__doc__, version='Shotgun Build Repository Clone Tool 0.1')

    is_dry_run = arguments["--dry-run"]

    if not ci.is_in_ci_environment():
        print("This script should be run only on a CI server.")
        return

    if qt.is_qt_required():
        _install_qt(is_dry_run)

    _install_tk_core(is_dry_run)
    _install_toolkit_frameworks(is_dry_run)


if __name__ == "__main__":
    main()
