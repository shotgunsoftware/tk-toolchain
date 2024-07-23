# Copyright (c) 2024 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Toolkit Build Qt resources

Compile Qt interface and resource files with a specified PySide compiler.

Usage:
    tk-build-qt-resources -y <yamlfile> (-p <pyenv> | [-u <uic>] [-r <rcc>])

Options:
    -y --yamlfile   The path to the YAML file with commands.
    -p --pyenv      The Python environment path.
    -u --uic        The PySide uic compiler.
    -r --rcc        The PySide rcc compiler.

Examples:
    tkbuild-qt-resources -y /path/to/yml/file/with/commands

    tkbuild-qt-resources -y /path/to/yml/file/with/commands -p /path/to/python/env

    tkbuild-qt-resources -y /path/to/yml/file/with/commands -u /path/to/pyside2-uic -r /path/to/pyside2-rcc
"""

import argparse
import os
import re
import subprocess

from ruamel.yaml import YAML

# Set the Python environment variable. If 'PYTHONPATH' is not set, use the default path "/usr/bin/"
# or you can override the Python environment path for a specific virtual environment
PYTHON_ENV = os.getenv("PYTHONPATH", "/usr/bin/")


def process_import_line(module, import_text):
    return (
        f"from {import_text} import {module}\n"
        f"for name, cls in {module}.__dict__.items():\n"
        f"    if isinstance(cls, type): globals()[name] = cls\n"
    )


def verify_compiler(compiler):
    try:
        print("Verifying compiler: ", compiler)
        return subprocess.check_output([compiler, "--version"], text=True).strip()

    except (FileNotFoundError, subprocess.CalledProcessError) as error:
        print(f"The PySide compiler version cannot be determine: {error}")


def build_qt(compiler, py_filename, py_built_path, import_text):
    output_path = f"{py_built_path}/{py_filename}.py"
    subprocess.run(compiler.split(" "), stdout=open(output_path, "w"), check=True)
    content = open(output_path, "r").read()
    content = re.sub(
        r"^from PySide2.QtWidgets(\s.*)?$", "", content, flags=re.MULTILINE
    )
    content = re.sub(r"^\s*$", "", content, flags=re.MULTILINE)
    content = re.sub(
        r"^from PySide2\.(\w+) import (.*)$",
        lambda m: process_import_line(m.group(1), import_text),
        content,
        flags=re.MULTILINE,
    )
    content = content.replace("from PySide2 import", f"from {import_text} import")
    open(output_path, "w").write(content)


def build_ui(
    compiler, qt_ui_path, py_built_path, import_text, filename, py_filename=None
):
    return {
        "compiler": f"{compiler} -g python --from-imports {qt_ui_path}/{filename}.ui",
        "py_filename": py_filename or filename,
        "py_built_path": py_built_path,
        "import_text": import_text,
    }


def build_res(
    compiler, qt_ui_path, py_built_path, import_text, filename, py_filename=None
):
    return {
        "compiler": f"{compiler} -g python {qt_ui_path}/{filename}.qrc",
        "py_filename": f"{py_filename or filename}_rc",
        "py_built_path": py_built_path,
        "import_text": import_text,
    }


def build_absolute_path(path1, path2):
    dir1 = os.path.dirname(path1)
    combined_path = os.path.normpath(os.path.join(dir1, path2))

    return combined_path


def run_yaml_commands(yaml_file, uic, rcc):
    with open(yaml_file, "r") as file:
        yaml = YAML()
        yaml_commands = yaml.load(file)

    for command_set in yaml_commands:
        try:
            build_params = {
                "qt_ui_path": build_absolute_path(yaml_file, command_set["ui_src"]),
                "py_built_path": build_absolute_path(yaml_file, command_set["py_dest"]),
                "import_text": command_set["import_pattern"],
            }
        except KeyError:
            print("'ui_src', 'py_dest' and 'import_pattern' are required in yml config")
            return 1

        print("Building user interfaces...")
        for index, ui_file in enumerate(command_set.get("ui_files", [])):
            build_params_ui_files = {
                **build_params,
                "compiler": uic,
                "filename": ui_file,
                "py_filename": (
                    command_set.get("new_names_ui_files", [])[index]
                    if command_set.get("new_names_ui_files", [])
                    else None
                ),
            }
            build_qt_params = build_ui(**build_params_ui_files)
            build_qt(**build_qt_params)

        print("Building resources...")
        for index, res_file in enumerate(command_set.get("res_files", [])):
            build_params_res_files = {
                **build_params,
                "compiler": rcc,
                "filename": res_file,
                "py_filename": (
                    command_set.get("new_names_res_files", [])[index]
                    if command_set.get("new_names_res_files", [])
                    else None
                ),
            }
            build_qt_params = build_res(**build_params_res_files)
            build_qt(**build_qt_params)


def main():
    parser = argparse.ArgumentParser(description="Build UI and resource files")
    parser.add_argument("-u", "--uic", help="The PySide uic compiler")
    parser.add_argument("-r", "--rcc", help="The PySide rcc compiler")
    parser.add_argument(
        "-p", "--pyenv", default=PYTHON_ENV, help="The Python environment path"
    )
    parser.add_argument(
        "-y",
        "--yamlfile",
        help="The path to the YAML file with commands",
        default="build_resources.yml"
    )
    args = parser.parse_args()

    if (not args.uic and not args.rcc) and args.pyenv:
        args.uic = f"{args.pyenv}/pyside2-uic"
        args.rcc = f"{args.pyenv}/pyside2-rcc"

    if not args.rcc or not args.uic:
        print(
            "The PySide rcc and uic compiler must be "
            "specified with the -u and -r parameters"
        )
        if not args.pyenv:
            print("or Python env must be specified with the -p parameter")
        return 1

    for compiler in [args.uic, args.rcc]:
        version = verify_compiler(compiler)
        if not version:
            return 1
        print(f"Using PySide compiler version: {version}")

    run_yaml_commands(args.yamlfile, args.uic, args.rcc)
