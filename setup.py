#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2019 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.
# -*- coding: utf-8 -*-

import os
import sys
import codecs
from setuptools import setup, find_packages


def read_file(fname):
    """
    Reads the specified text file and returns it's contents.

    :returns: The text content.
    """
    file_path = os.path.join(os.path.dirname(__file__), fname)
    with codecs.open(file_path, encoding="utf-8") as fh:
        return fh.read()


setup(
    name="tk-toolchain",
    version="0.2.1.dev",
    author="Autodesk",
    author_email="https://developers.shotgridsoftware.com",
    maintainer="Autodesk",
    maintainer_email="https://developers.shotgridsoftware.com",
    license=read_file("LICENSE"),
    url="https://github.com/shotgunsoftware/tk-toolchain",
    description="Build tools for Flow Production Tracking Toolkit.",
    long_description=read_file("README.md"),
    packages=find_packages(),
    data_files=[("", ["LICENSE"])],
    package_data={
        "tk_toolchain": [
            os.path.join("tk_testengine", "*"),
            os.path.join("cmd_line_tools", "tk_docs_generation", "sphinx_data", "*"),
            os.path.join("cmd_line_tools", "tk_run_app", "config", "env", "*"),
            os.path.join("cmd_line_tools", "tk_run_app", "config", "core", "*"),
            os.path.join(
                "cmd_line_tools", "tk_run_app", "config", "core", "hooks", "*"
            ),
            os.path.join(
                "cmd_line_tools", "tk_docs_generation", "sphinx_data", "_static", "*"
            ),
            os.path.join(
                "cmd_line_tools", "tk_docs_generation", "sphinx_data", "_templates", "*"
            ),
            os.path.join(
                "cmd_line_tools", "tk_docs_generation", "sphinx_data", "resources", "*"
            ),
        ]
    },
    python_requires=">=3.7.0",
    install_requires=[
        # Tests
        "pytest==7.4.2",
        "pytest-cov==4.1.0",
        # Locking down these 2 tools to these specific versions is important
        # because we should use the same tools that tk-core ships with.
        "mock==5.1.0",
        "coverage==7.2.7",
        # Doc generation
        "PyYAML",
        "sphinx==7.0.0" if sys.version_info[0:2] >= (3, 9) else "sphinx==5.3.0",
        "sphinx_rtd_theme==1.3.0",
        "docopt==0.6.2",
        "six==1.14.0",
        # Lock down jinja because 3.1.0 breaks the build.
        "jinja2==3.0.3",
        # Other tools used by devs that are useful to have.
        "pre-commit",
        "ruamel.yaml",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={
        "pytest11": ["pytest_tank_test = pytest_tank_test"],
        "console_scripts": [
            "tk-docs-preview = tk_toolchain.cmd_line_tools.tk_docs_generation:main",
            "tk-run-app = tk_toolchain.cmd_line_tools.tk_run_app:main",
            "tk-config-update = tk_toolchain.cmd_line_tools.tk_config_update:main",
        ],
    },
)
