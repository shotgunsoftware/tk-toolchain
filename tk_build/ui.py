# Copyright (c) 2018 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from __future__ import print_function
from memoize import memoize
import subprocess
import sys
import os
import re

# Remove any problematic profiles from pngs.
# for f in *.png; do mogrify $f; done


def _get_pyside_uic_name():
    if sys.platform == "win32":
        return "pyside-uic.exe"
    else:
        return "pyside-uic"


def _get_pyside_rcc_name():
    if sys.platform == "win32":
        return "pyside-rrc.exe"
    else:
        return "pyside-rrc"


@memoize
def _get_pyside_scripts_folder():
    """
    Finds
    """
    if sys.platform == "win32":
        desktop_path = "C:\\Program Files\\Shotgun\\Python\\Scripts\\"
    elif sys.platform == "darwin":
        desktop_path = "/Applications/Shotgun.app/Contents/Resources/Python/bin"
    elif sys.platform.startswith("linux"):
        desktop_path = "/opt/Shotgun/Python/bin"

    if os.path.exists(desktop_path):
        return desktop_path
    else:
        return os.path.dirname(sys.executable)


def _build_file(command_line):
    # Prepend the path to the python interpreter
    command_line[0] = os.path.join(_get_pyside_scripts_folder(), command_line[0])
    return subprocess.check_output(command_line)


def _filter_output(text_output):
    text_output = text_output.split("\n")

    text_output = [
        re.sub(
            "from PySide import",
            "from sgtk.platform.qt import",
            line
        ) for line in text_output if line.startswith("# Created:") is False
    ]

    return "\n".join(text_output)


def _build_qt(command_line, output_folder, output_file):

    print(" > Building %s" % output_file)

    text_output = _build_file(command_line)
    text_output = _filter_output(text_output)

    output_path = os.path.join(output_folder, output_file)

    with open("%s.py" % output_path, "w") as fd:
        fd.write(text_output)


def build_ui(output_folder, ui_files):
    if not isinstance(ui_files, list):
        ui_files = [ui_files]

    for ui_file in ui_files:
        _build_qt(
            ["pyside-uic", "--from-imports", "{0}.ui".format(ui_file)],
            output_folder,
            ui_file
        )


def _mogrify_pngs(resource_file_name):
    pass


def build_resource(resource_file_name):

    _mogrify_pngs(resource_file_name)
