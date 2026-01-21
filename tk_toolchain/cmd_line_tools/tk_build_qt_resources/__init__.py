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
    tk-build-qt-resources [-y <yamlfile>] (-p <pyenv> | [-u <uic>] [-r <rcc>])

Options:
    -y --yamlfile   The path to the YAML file with commands.
    -p --pyenv      The Python environment path.
    -u --uic        The PySide uic compiler.
    -r --rcc        The PySide rcc compiler.

Examples:
    tk-build-qt-resources

    tk-build-qt-resources -y name_of_yml_file_with_commands.yml

    tk-build-qt-resources -p /path/to/python/env

    tk-build-qt-resources -u /path/to/pyside2-uic -r /path/to/pyside2-rcc
"""

import argparse
import os
import re
import subprocess
import sys

from ruamel.yaml import YAML


# Store the supported versions in a tuple
PYSIDE_VERSIONS = ("PySide2", "PySide6")
QT_MODULES = ["QtCore", "QtGui", "QtWidgets"]


def verify_compiler(compiler):
    try:
        print("Verifying compiler: ", compiler)
        return subprocess.check_output([compiler, "--version"], text=True).strip()

    except (FileNotFoundError, subprocess.CalledProcessError) as error:
        print(f"The PySide compiler version cannot be determine: {error}")


def process_import_block(module, import_text):
    return (
        f"from {import_text} import {module}\n"
        f"for name, cls in {module}.__dict__.items():\n"
        f"    if isinstance(cls, type): globals()[name] = cls\n"
    )


def add_import_block_after_header(file_content, import_block):
    lines = file_content.splitlines()
    index = 0

    while index < len(lines) and (lines[index].strip().startswith("#") or lines[index].strip() == ""):
        index += 1

    header = "\n".join(lines[:index]).rstrip()
    body = "\n".join(lines[index:]).lstrip()

    return f"{header}\n\n{import_block.strip()}\n\n{body}\n"


def build_qt(compiler, py_filename, py_built_path, import_text):
    output_path = os.path.join(py_built_path, f"{py_filename}.py")
    with open(output_path, "w") as out_file:
        subprocess.run(compiler.split(" "), stdout=out_file, check=True)

    with open(output_path, "r") as py_file:
        content = py_file.read()

    # Check which PySide version is being used
    pyside_version = next((version for version in PYSIDE_VERSIONS if version in content), None)
    if not pyside_version:
        return

    def remove_qt_imports(file_content, module):
        """
        Remove Qt import lines from the given module, including parenthesised and multi-line formats.
        """
        imports_with_parenthesis = rf"from {pyside_version}\.{module} import\s*\((?:.|\n)*?\)\s*"
        file_content = re.sub(imports_with_parenthesis, "", file_content, flags=re.MULTILINE)

        inline_imports_submodule = rf"from {pyside_version}\.{module} import [^\n]+(?:\n[ \t]+[^\n]+)*"
        file_content = re.sub(inline_imports_submodule, "", file_content, flags=re.MULTILINE)

        inline_imports_root = rf"from {pyside_version} import [^\n]+(?:\n[ \t]+[^\n]+)*"
        file_content = re.sub(inline_imports_root, "", file_content, flags=re.MULTILINE)

        return file_content

    # Remove Qt module imports
    for qt_module in QT_MODULES:
        content = remove_qt_imports(content, qt_module)

    # Remove any leftover lines
    content = re.sub(
        r"^\s*[A-Za-z_][A-Za-z0-9_]*(\s*,\s*[A-Za-z_][A-Za-z0-9_]*)*\s*\)?\s*$",
        "",
        content,
        flags=re.MULTILINE,
    )
    # Remove blank lines
    content = re.sub(r"\n\s*\n", "\n", content).strip()

    # Create the new imports
    import_block = (
        process_import_block("QtCore", import_text) + "\n" +
        process_import_block("QtGui", import_text)
    )

    final_content = add_import_block_after_header(content, import_block)

    with open(output_path, "w") as py_file:
        py_file.write(final_content)


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


def build_absolute_path(path_or_file):
    dir = os.getcwd()
    combined_path = os.path.normpath(os.path.join(dir, path_or_file))

    return combined_path


def run_yaml_commands(yaml_file, uic, rcc):
    yaml = YAML()
    yaml_commands = yaml.load(open(build_absolute_path(yaml_file)))

    for command_set in yaml_commands:
        ui_src = command_set.get("ui_src")
        if not ui_src:
            print("'ui_src' is required in yml config")
            sys.exit(1)

        build_params = {
            "qt_ui_path": build_absolute_path(ui_src),
            "py_built_path": build_absolute_path(command_set.get("py_dest", ui_src)),
            "import_text": command_set.get("import_pattern", "tank.platform.qt"),
        }

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

    return 1


def main():
    parser = argparse.ArgumentParser(description="Build UI and resource files")
    parser.add_argument("-u", "--uic", help="The PySide uic compiler")
    parser.add_argument("-r", "--rcc", help="The PySide rcc compiler")
    parser.add_argument(
        "-p",
        "--pyenv",
        default=os.getenv("PYTHONPATH"),
        help="The Python environment path",
    )
    parser.add_argument(
        "-y",
        "--yamlfile",
        default="build_resources.yml",
        help="The path to the YAML file with commands",
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
