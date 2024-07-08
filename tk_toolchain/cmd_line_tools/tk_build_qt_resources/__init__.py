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
    tk-build-qt-resources (-p <pyenv> | [-u <uic>] [-r <rcc>]) -q <qtuipath> -py <pybuiltpath> -uf <uifiles>... [-ufn <uifilenames>...] -rf <resfiles>... [-rfn <resfilenames>...] [-i <importtext>]

Options:
    -u --uic        The PySide uic compiler.
    -r --rcc        The PySide rcc compiler.
    -p --pyenv      The Python environment path.
    -q --qtuipath   The path with Qt .ui files.
    -py --pybuiltpath The path to output all built .py files.
    -uf --uifiles   The Qt .ui files to compile.
    -ufn --uifilenames   Specific Qt .ui file names to compile.
    -rf --resfiles  The Qt .qrc resource files to compile.
    -rfn --resfilenames  Specific Qt .qrc file names to compile.
    -i --importtext The import text to replace (default is "tank.platform.qt").

Examples:
    tkbuild-qt-resources -u /path/to/pyside2-uic -r /path/to/pyside2-rcc -q /path/to/qt/ui/files -py /path/to/output/py/files -uf file1 file2 -rf resource1 resource2 -i custom.import.path

    tkbuild-qt-resources -p /path/to/python/env -q /path/to/qt/ui/files -py /path/to/output/py/files -uf file1 file2 -rf resource1 resource2 -i custom.import.path

    tkbuild-qt-resources -p /path/to/python/env -q /path/to/qt/ui/files -py /path/to/output/py/files -uf file1 file2 -ufn ui_file1 ui_file2 -rf resource1 resource2 -i custom.import.path
"""

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
        return subprocess.check_output([compiler, "--version"], text=True).strip()

    except (FileNotFoundError, subprocess.CalledProcessError) as error:
        print(f"The PySide compiler version cannot be determine: {error}")


def build_qt(compiler, py_filename, py_built_path, import_text):
    print(f"The import text to replace will be '{import_text}'")
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


def main():
    parser = argparse.ArgumentParser(description="Build UI and resource files")
    parser.add_argument("-u", "--uic", help="The PySide uic compiler")
    parser.add_argument("-r", "--rcc", help="The PySide rcc compiler")
    parser.add_argument("-p", "--pyenv", help="The Python environment path")
    parser.add_argument(
        "-q",
        "--qtuipath",
        required=True,
        help="The path with resources Qt .ui files",
    )
    parser.add_argument(
        "-py",
        "--pybuiltpath",
        required=True,
        help="The path to output all built .py files to",
    )
    parser.add_argument(
        "-uf",
        "--uifiles",
        nargs="+",
        required=True,
        help="The Qt .ui files to compile.",
    )
    parser.add_argument(
        "-ufn",
        "--uifilenames",
        nargs="+",
        help="Specific Qt .ui file names to compile.",
    )
    parser.add_argument(
        "-rf",
        "--resfiles",
        nargs="+",
        required=True,
        help="The Qt .qrc resource files to compile.",
    )
    parser.add_argument(
        "-rfn",
        "--resfilenames",
        nargs="+",
        help="Specific Qt .qrc file names to compile.",
    )
    parser.add_argument(
        "-i",
        "--importtext",
        default="tank.platform.qt",
        help="The import text to replace",
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

    build_params = {
        "qt_ui_path": args.qtuipath,
        "py_built_path": args.pybuiltpath,
        "import_text": args.importtext,
    }

    print("Building user interfaces...")
    for index, ui_file in enumerate(args.uifiles):
        build_params_ui_files = build_params.copy()
        build_params_ui_files["compiler"] = args.uic
        build_params_ui_files["filename"] = ui_file
        if args.uifilenames:
            build_params_ui_files["py_filename"] = args.uifilenames[index]
        build_qt_params = build_ui(**build_params_ui_files)
        build_qt(**build_qt_params)

    print("Building resources...")
    for index, res_file in enumerate(args.resfiles):
        build_params_res_files = build_params.copy()
        build_params_res_files["compiler"] = args.rcc
        build_params_res_files["filename"] = res_file
        if args.resfilenames:
            build_params_res_files["py_filename"] = args.resfilenames[index]
        build_qt_params = build_res(**build_params_res_files)
        build_qt(**build_qt_params)
