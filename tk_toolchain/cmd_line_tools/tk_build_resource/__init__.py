#!/usr/bin/env python3

import subprocess
import argparse
import re


def process_import_line(module, import_text):
    return (
        f'from {import_text} import {module}\n'
        f'for name, cls in {module}.__dict__.items():\n'
        f'    if isinstance(cls, type): globals()[name] = cls\n'
    )


def verify_compiler(compiler):
    try:
        print("Verifying compiler: ", compiler)
        version_compiler = subprocess.check_output([compiler, "--version"], text=True).strip()
        return True, version_compiler
    except Exception as error:
        return False, error


def build_qt(compiler, output, py_built_path, import_text):
    print(f"The import text to replace will be '{import_text}'")
    output_path = f"{py_built_path}/{output}.py"
    with open(output_path, 'w') as output_file:
        subprocess.run(compiler.split(" "), stdout=output_file, check=True)
    with open(output_path, 'r') as file:
        content = file.read()
    content = re.sub(r'^from PySide2.QtWidgets(\s.*)?$', '', content, flags=re.MULTILINE)
    content = re.sub(r'^\s*$', '', content, flags=re.MULTILINE)
    content = re.sub(
        r'^from PySide2\.(\w+) import (.*)$',
        lambda m: process_import_line(m.group(1), import_text),
        content,
        flags=re.MULTILINE
    )
    content = content.replace('from PySide2 import', f'from {import_text} import')
    with open(output_path, 'w') as file:
        file.write(content)


def build_ui(compiler, qt_ui_path, py_built_path, import_text, name):
    build_qt(
        f"{compiler} -g python --from-imports {qt_ui_path}/{name}.ui",
        name,
        py_built_path,
        import_text
    )


def build_res(compiler, qt_ui_path, py_built_path, import_text, name):
    build_qt(f"{compiler} -g python {qt_ui_path}/{name}.qrc", f"{name}_rc", py_built_path, import_text)


def main():
    parser = argparse.ArgumentParser(description="Build UI and resource files.")
    parser.add_argument("-u", "--uic", type=str, help="The PySide uic compiler")
    parser.add_argument("-r", "--rcc", type=str, help="The PySide rcc compiler")
    parser.add_argument("-p", "--pyenv", type=str, help="The Python environment path")
    parser.add_argument(
        "-q",
        "--quipath",
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
        "-i",
        "--importtext",
        default="tank.platform.qt",
        type=str,
        help="The import text to replace"
    )
    args = parser.parse_args()
    uic = args.uic
    rcc = args.rcc
    pyenv = args.pyenv
    qt_ui_path = args.quipath
    import_text = args.importtext
    py_built_path = args.pybuiltpath

    if (not uic and not uic) and pyenv:
        uic = f"{pyenv}/pyside2-uic"
        rcc = f"{pyenv}/pyside2-rcc"
    if not rcc or not uic:
        print("The PySide rcc and uic compiler must be specified with the -u and -r parameters")
        if not pyenv:
            print("or Python env must be specified with the -p parameter")
        return
    for compiler in [uic, rcc]:
        verified, version_or_error = verify_compiler(compiler)
        if not verified:
            print(f"The PySide compiler version cannot be determine: {version_or_error}")
            return
        print(f"Using PySide compiler version: {version_or_error}")

    print("Building user interfaces...")
    build_ui(uic, qt_ui_path, py_built_path, import_text, "login_dialog")
    print("Building resources...")
    build_res(rcc, qt_ui_path, py_built_path, import_text, "resources")


if __name__ == "__main__":
    main()
