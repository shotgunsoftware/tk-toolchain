
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

from docopt import docopt

from tk_build import ci, qt


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
            commands.append(["sudo", "apt-get", "install", "libqt4-dev"])

        commands.append(
            ["pip", "install", "{}=={}".format(qt_lib, qt_version),
             "--no-index", "--find-links", "https://parkin.github.io/python-wheelhouse/"],
        )

        if qt.is_pyside1_required():
            # PySide needs to be patched after install so we need to finish the install by the following
            commands.append([
                "python",
                os.path.expandvars("~/virtualenv/python${TRAVIS_PYTHON_VERSION}/bin/pyside_postinstall.py -install")
            ])

        # Now we need to start the X server...
        # Taken from:
        # https://github.com/colmap/colmap/commit/606d3cd09931d78a3272f99b5e7a2cb6894e243e
        commands.append(
            ["sh", "-e /etc/init.d/xvfb start"]
        )

        # update the environment variables to be able to run Qt
        env = {}
        env.update(os.environ)
        env.update(qt.get_runtime_env_vars())

        for cmd in commands:
            print("Running:", " ".join(cmd))
            if not is_dry_run:
                subprocess.check_call(cmd, env)

        if not is_dry_run:
            # Let the x server time to start.
            time.sleep(3)
    else:
        print("Qt will not be initialized for {}.".format(ci.get_ci_name()))


def main():

    arguments = docopt(__doc__, version='Shotgun Build Repository Clone Tool 0.1')

    is_dry_run = arguments["--dry-run"]

    if not ci.is_in_ci_environment():
        print("This script should be run only on a CI server.")
        return

    if qt.is_qt_required():
        _install_qt(is_dry_run)

if __name__ == "__main__":
    main()
