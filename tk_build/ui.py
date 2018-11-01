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
import traceback
import sys
import os
import glob
import re


def _get_pyside_uic_name():
    """
    Returns the name of the executable that can convert .ui files into .py
    files.
    """
    if sys.platform == "win32":
        return "pyside-uic.exe"
    else:
        return "pyside-uic"


def _get_pyside_rcc_name():
    """
    Returns the name of the executable that can convert .qrc files into .py
    files.
    """
    if sys.platform == "win32":
        return "pyside-rcc.exe"
    else:
        return "pyside-rcc"


def _get_caller_folder():
    """
    Returns the first caller of a method inside this module. This
    method needs to be called by a method called build_resources or
    build_ui.
    """

    # -1 is this function
    # -2 is build_resources or build_ui
    # -3 is the build_resources.py script.
    return os.path.dirname(traceback.extract_stack()[-3][0])


@memoize
def _get_pyside_scripts_folder():
    """
    Finds a Python which has PySide.

    First tries to find the Shotgun Desktop, then tries the current Python.

    If nothing was found, this method raises a RuntimeError.
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
        try:
            from PySide import QtGui # noqa
        except ImportError:
            raise RuntimeError(
                "Couldn't find a copy of Python which has PySide. You can solve "
                "this problem by installing the Shotgun Desktop in the default location."
            )
        else:
            return os.path.dirname(sys.executable)


def _build_file(command_line, execution_folder):
    """
    Invokes a tool in a given folder.

    :param str command_line: Tool to execute.
    :param str execution_folder: Folder to execute the tool in.

    :returns: The text output of the tool.
    """
    # Prepend the path to the python interpreter
    command_line[0] = os.path.join(_get_pyside_scripts_folder(), command_line[0])
    return subprocess.check_output(command_line, cwd=execution_folder)


def _filter_output(text_output):
    """
    Takes a block of text and parses it to rewrite Qt imports and remove
    the creation time.

    :param str text_output: Block on text to filter.

    :returns: Block of filtered text.
    """
    text_output = text_output.split("\n")

    text_output = [
        re.sub(
            "from PySide import",
            "from sgtk.platform.qt import",
            line
        ) for line in text_output if line.startswith("# Created:") is False
    ]

    return "\n".join(text_output)


def _build_qt(command_line, output_folder, output_file, execution_folder):
    """
    Runs a tool, captures it's output and writes it to the specified file.

    :param str command_line: Tool to execute.
    :param str output_folder: Folder in which the file will be written to.
    :param str input_file: File that needs to be converted.
    :param str execution_folder: Folder in which to run the tool.
    """
    print(" > Building %s" % output_file)

    text_output = _build_file(command_line, execution_folder)
    text_output = _filter_output(text_output)

    output_path = os.path.join(output_folder, os.path.basename(output_file))
    with open("%s.py" % os.path.join(execution_folder, output_path), "w") as fd:
        fd.write(text_output)


def build_ui(output_folder, ui_files):
    """
    Builds one or multiple .ui files and writes them to the specified folder.

    :param str output_folder: Folder in which to output the files.
    :param list(str) or str: One or multiple files, without the .ui extension
        to convert into .py files.
    """
    execution_folder = _get_caller_folder()

    if not isinstance(ui_files, list):
        ui_files = [ui_files]

    for ui_file in ui_files:
        _build_qt(
            [_get_pyside_uic_name(), "--from-imports", "{0}.ui".format(ui_file)],
            output_folder,
            ui_file,
            execution_folder
        )


def _mogrify_pngs(execution_folder):
    """
    Runs the mogriphy tool on all the png files in order to remove dubious
    profiles.
    """
    for png_file in glob.iglob(os.path.join(execution_folder, "*.png")):
        subprocess.check_output(["mogrify", png_file])


def build_resource(output_folder, resource_file_name="resources"):
    """
    Builds a qrc file and writes it to the specified folder.

    :param str output_folder: Folder in which to output the file.
    :param str resource_file_name: File that needs to be converted, without the qrc extension. Defaults to resources.
    """
    execution_folder = _get_caller_folder()
    _mogrify_pngs(execution_folder)

    _build_qt(
        [_get_pyside_rcc_name(), "%s.qrc" % resource_file_name],
        output_folder,
        "%s_rc" % resource_file_name,
        execution_folder
    )
