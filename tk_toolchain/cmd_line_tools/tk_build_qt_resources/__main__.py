#!/usr/bin/env python3
# Copyright (c) 2024 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

####################################################################################

import argparse
import re
import subprocess


def process_import_line(module, import_text):
    return (
        f"from {import_text} import {module}\n"
        f"for name, cls in {module}.__dict__.items():\n"
        f"    if isinstance(cls, type): globals()[name] = cls\n"
    )


def verify_compiler(compiler):
    try:
        print("Verifying compiler: ", compiler)
        version_compiler = subprocess.check_output(
            [compiler, "--version"],
            text=True
        ).strip()
        return True, version_compiler
    except Exception as error:
        return False, error


def build_qt(compiler, output, py_built_path, import_text):
    print(f"The import text to replace will be '{import_text}'")
    output_path = f"{py_built_path}/{output}.py"
    subprocess.run(
        compiler.split(" "),
        stdout=open(output_path, "w"),
        check=True
    )
    content = open(output_path, 'r').read()
    content = re.sub(
        r'^from PySide2.QtWidgets(\s.*)?$',
        '',
        content,
        flags=re.MULTILINE
    )
    content = re.sub(r'^\s*$', '', content, flags=re.MULTILINE)
    content = re.sub(
        r'^from PySide2\.(\w+) import (.*)$',
        lambda m: process_import_line(m.group(1), import_text),
        content,
        flags=re.MULTILINE
    )
    content = content.replace(
        'from PySide2 import',
        f'from {import_text} import'
    )
    open(output_path, 'w').write(content)


def build_ui(compiler, qt_ui_path, py_built_path, import_text, name):
    build_qt(
        f"{compiler} -g python --from-imports {qt_ui_path}/{name}.ui",
        name,
        py_built_path,
        import_text
    )


def build_res(compiler, qt_ui_path, py_built_path, import_text, name):
    build_qt(
        f"{compiler} -g python {qt_ui_path}/{name}.qrc",
        f"{name}_rc",
        py_built_path,
        import_text
    )


def main():
    parser = argparse.ArgumentParser(description="Build UI and resource files")
    parser.add_argument(
        "-u",
        "--uic",
        type=str, help="The PySide uic compiler"
    )
    parser.add_argument(
        "-r",
        "--rcc",
        type=str,
        help="The PySide rcc compiler"
    )
    parser.add_argument(
        "-p",
        "--pyenv",
        type=str,
        help="The Python environment path"
    )
    parser.add_argument(
        "-q",
        "--qtuipath",
        type=str,
        required=True,
        help="The path with resources Qt .ui files"
    )
    parser.add_argument(
        "-py",
        "--pybuiltpath",
        type=str,
        required=True,
        help="The path to output all built .py files to"
    )
    parser.add_argument(
        "-uf",
        "--uifiles",
        nargs='+',
        required=True,
        help="The path with resources Qt .ui files"
    )
    parser.add_argument(
        "-rf",
        "--resfiles",
        nargs='+',
        required=True,
        help="The path to output all built .py files to"
    )
    parser.add_argument(
        "-i",
        "--importtext",
        default="tank.platform.qt",
        type=str,
        help="The import text to replace"
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
        verified, version_or_error = verify_compiler(compiler)
        if not verified:
            print(
                "The PySide compiler version cannot be "
                f"determine: {version_or_error}"
            )
            return 1
        print(f"Using PySide compiler version: {version_or_error}")

    print("Building user interfaces...")
    for ui_file in args.uifiles:
        build_ui(
            args.uic,
            args.qtuipath,
            args.pybuiltpath,
            args.importtext,
            ui_file
        )

    print("Building resources...")
    for res_file in args.resfiles:
        build_res(
            args.rcc,
            args.qtuipath,
            args.pybuiltpath,
            args.importtext,
            res_file
        )
