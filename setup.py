#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup, find_packages


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='tk-build',
    version='0.1.0',
    author='Shotgun Software',
    author_email='support@shotgunsoftware.com',
    maintainer='Shotgun Software',
    maintainer_email='support@shotgunsoftware.com',
    license='MIT',
    url='https://github.com/shotgunsoftware/tk-build',
    description='Build tools for Shotgun Toolkit.',
    long_description=read('README.rst'),
    # package_dir={"tk_build": "tk_build"},
    # py_modules=['pytest_tk_build'],
    packages=find_packages(),
    package_data={'tk_build': ['cmd_line_tools/tk_docs/sphinx_data/*']},

    python_requires='~=2.7.0',
    install_requires=[
        # Framework
        'memoize2~=0.1.1',
        "docopt",

        # Tests
        'pytest>=3.5.0',
        'pytest-cov==2.6.0',
        "mock",
        "coverage==4.4.1",
        "unittest2",
        "coveralls==1.1",

        # Doc generation
        "PyYAML",
        "sphinx",
        "sphinx_rtd_theme"
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={
        'pytest11': [
            'pytest_tk_build = pytest_tk_build',
        ],
        'console_scripts': [
            'tk-clone = tk_build.cmd_line_tools.sg_clone:sg_clone',
            'tk-docs = tk_build.cmd_line_tools.tk_docs:main',
            'tk-ci-tests = tk_build.cmd_line_tools.tk_ci_tests:main',
            'tk-ci-install = tk_build.cmd_line_tools.tk_ci_install:main'
        ]
    }
)
