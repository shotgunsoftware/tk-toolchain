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
            [compiler, "--version"], text=True
        ).strip()
        return version_compiler

    except (FileNotFoundError, subprocess.CalledProcessError) as error:
        print(
            "The PySide compiler version cannot be "
            f"determine: {error}"
        )
        return False


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


def build_ui(compiler, qt_ui_path, py_built_path, import_text, filename):
    return {
        "compiler": f"{compiler} -g python --from-imports {qt_ui_path}/{filename}.ui",
        "py_filename": filename,
        "py_built_path": py_built_path,
        "import_text": import_text,
    }


def build_res(compiler, qt_ui_path, py_built_path, import_text, filename):
    return {
        "compiler": f"{compiler} -g python {qt_ui_path}/{filename}.qrc",
        "py_filename": f"{filename}_rc",
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
        help="The path with resources Qt .ui files",
    )
    parser.add_argument(
        "-rf",
        "--resfiles",
        nargs="+",
        required=True,
        help="The path to output all built .py files to",
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
    for ui_file in args.uifiles:
        build_params["compiler"] = args.uic
        build_params["filename"] = ui_file
        build_qt_params = build_ui(**build_params)
        build_qt(**build_qt_params)

    print("Building resources...")
    for res_file in args.resfiles:
        build_params["compiler"] = args.rcc
        build_params["filename"] = res_file
        build_qt_params = build_res(**build_params)
        build_qt(**build_qt_params)
