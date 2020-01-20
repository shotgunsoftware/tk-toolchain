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


python_version = sys.version_info[0:2]
is_python_3 = python_version[0] == 3
is_python_27_or_greater = python_version >= (2, 7)
is_python_27 = python_version == (2, 7)
is_python_2 = python_version[0] == 2


setup(
    name="tk-toolchain",
    version="0.1.0.dev",
    author="Shotgun Software",
    author_email="support@shotgunsoftware.com",
    maintainer="Shotgun Software",
    maintainer_email="support@shotgunsoftware.com",
    license=read_file("LICENSE"),
    url="https://github.com/shotgunsoftware/tk-toolchain",
    description="Build tools for Shotgun Toolkit.",
    long_description=read_file("README.md"),
    packages=find_packages(),
    data_files=[("", ["LICENSE"])],
    package_data={
        "tk_toolchain": [
            os.path.join("tk_testengine", "*"),
            os.path.join("cmd_line_tools", "tk_docs_preview", "sphinx_data", "*"),
            os.path.join("cmd_line_tools", "tk_run_app", "config", "env", "*"),
            os.path.join("cmd_line_tools", "tk_run_app", "config", "core", "*"),
            os.path.join(
                "cmd_line_tools", "tk_run_app", "config", "core", "hooks", "*"
            ),
            os.path.join(
                "cmd_line_tools", "tk_docs_preview", "sphinx_data", "_static", "*"
            ),
        ]
    },
    python_requires=">=2.6.0",
    install_requires=[
        # Tests
        "pytest==4.6.6" if is_python_27_or_greater else "pytest<3.3",
        "pytest-cov==2.6.1" if is_python_27_or_greater else "pytest-cov==2.5.1",
        # Locking down these 3 tools to these specific versions is important
        # because we should use the same tools that tk-core ships with.
        "mock==2.0.0",
        "coverage==4.5.4",
        "unittest2==1.1.0",
        # Doc generation
        "PyYAML" if is_python_27_or_greater else "PyYAML==3.11",
        # sphinx 2.0 is Python 3 only, so we have to cap out the version
        # we use on Python 2.
        "sphinx"
        if is_python_3
        else ("sphinx<=1.8.5" if is_python_27 else "sphinx==1.4.9"),
        "sphinx_rtd_theme",
        "docopt",
    ]
    # Other tools used by devs that are useful to have.
    + (["pre-commit"] if is_python_27_or_greater else []),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={
        "pytest11": ["pytest_tank_test = pytest_tank_test"],
        "console_scripts": [
            "tk-docs-preview = tk_toolchain.cmd_line_tools.tk_docs_preview:main",
            "tk-run-app = tk_toolchain.cmd_line_tools.tk_run_app:main",
        ],
    },
)
