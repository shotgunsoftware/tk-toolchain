[![VFX Platform](https://img.shields.io/badge/vfxplatform-2024%20%7C%202023%20%7C%202022%20%7C%202021-blue.svg)](http://www.vfxplatform.com/)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.10%20%7C%203.9%20%7C%203.7-blue.svg)](https://www.python.org/)
[![Build Status](https://dev.azure.com/shotgun-ecosystem/Toolkit/_apis/build/status/tk-toolchain?repoName=shotgunsoftware%2Ftk-toolchain&branchName=master)](https://dev.azure.com/shotgun-ecosystem/Toolkit/_build/latest?definitionId=66&repoName=shotgunsoftware%2Ftk-toolchain&branchName=master)
[![codecov](https://codecov.io/gh/shotgunsoftware/tk-toolchain/branch/master/graph/badge.svg)](https://codecov.io/gh/shotgunsoftware/tk-toolchain)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Toolkit Build tools](#toolkit-build-tools)
- [What can it do?](#what-can-it-do)
- [How can I install `tk-toolchain`?](#how-can-i-install-tk-toolchain)
  - [Installing the `master` branch from GitHub](#installing-the-master-branch-from-github)
  - [Installing for development or debugging](#installing-for-development-or-debugging)
- [Pre-requisites](#pre-requisites)
- [How can I run these tools?](#how-can-i-run-these-tools)
- [Tools](#tools)
  - [`pre-commit`](#pre-commit)
  - [`pytest`](#pytest)
    - [Cheatsheet](#cheatsheet)
    - [Toolkit's `pytest` plugin, `pytest_tanktest`](#toolkits-pytest-plugin-pytest_tanktest)
      - [Adds the Toolkit core to the `PYTHONPATH`](#adds-the-toolkit-core-to-the-pythonpath)
      - [Exposes the common folder for all your repositories](#exposes-the-common-folder-for-all-your-repositories)
      - [Adds any Python modules for your tests into the `PYTHONPATH`](#adds-any-python-modules-for-your-tests-into-the-pythonpath)
      - [Configures a Toolkit log file for your tests](#configures-a-toolkit-log-file-for-your-tests)
      - [Provides a test engine](#provides-a-test-engine)
      - [Detects missing repositories](#detects-missing-repositories)
  - [`tk-docs-preview`](#tk-docs-preview)
  - [`tk-run-app`](#tk-run-app)
  - [`tk-config-update`](#tk-config-update)
  - [`tk-build-qt-resources`](#tk-build-qt-resources)
- [FAQ](#faq)
  - [When I run `tk-run-app` or `tk-docs-preview`, I get `command not found: tk-run-app`](#when-i-run-tk-run-app-or-tk-docs-preview-i-get-command-not-found-tk-run-app)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Toolkit Build tools

The Toolkit Build tools will help developers of Toolkit-based applications in their day to day development tasks. It is meant to be installed as a pip package and can be used both locally or on a continuous integration service to validate their code and documentation.

# What can it do?

By installing `tk-toolchain`, you will get the following tools:

`tk-docs-preview`: This tool allows to preview the documentation in the `docs` folder of a Toolkit application.

`tk-run-app`: This tool allows you to run most Toolkit application from the command line and launch it's GUI.

Also, the following standard Python tools will be installed:

`pytest`: [pytest](https://docs.pytest.org/en/latest/) is a test runner that is much more flexible than the old test runner that was packaged with tk-core.

`pre-commit`: [Pre-commit](https://pre-commit.com) is a tool that allows developers to run validators and reformatters before committing code to git, ensuring quality and consistency in a code base.

# How can I install `tk-toolchain`?

## Installing the `master` branch from GitHub

If you wish to install the current `master` branch, use the following command:

```
pip install git+https://github.com/shotgunsoftware/tk-toolchain.git#egg=tk-toolchain
```

or

```
pip install https://github.com/shotgunsoftware/tk-toolchain/archive/master.zip
```

> You can replace `master` with any development branch.

## Installing for development or debugging

If you want to add a feature or debug the package, first clone the repository and then use the following command inside it:

```
pip install -e .
```

Any changes you make will immediately be accessible from the package.

# Pre-requisites

These tools assume that all your Toolkit-based repositories are in the same folder. For example:

```
/home/yourlogin/git-repos/tk-core
/home/yourlogin/git-repos/tk-multi-publish2
/home/yourlogin/git-repos/tk-framework-shotgunutils
...
```

This allows the tools to quickly find other repositories they might need to run.

You also need to have a copy of the Python 3 interpreter available or the `black` code formatter won't be able to run. If you are using macOS or Linux, we highly recommend you use `pyenv`. You can install it on macOS via `brew` or your favorite package manager on Linux. On Windows, download Python 3 from [python.org](https://www.python.org)

# How can I run these tools?

- Type `pytest` to run the unit tests inside any Toolkit repository.
- Type `tk-docs-preview` to preview the documentation in the `docs` folder of your Toolkit application's repository.
- Type `tk-run-app` to launch the application from the current repository.

# Tools

## `pre-commit`

The pre-commit hook should be run on all Toolkit repositories in order to keep code quality as high as possible. The most important of the pre-commit hooks is the `black` code formatter, which will take care of formatting your code according to PEP8 so you don't have to think about it. Only the files that have been modified will be reformatted.

In you've just cloned a repository, type `pre-commit install` so that the hook is executed every single time you commit to `git` in the future.

If you're setting up a new repository, or if the repository you're about to work in does not have a file named `.pre-commit-config.yaml`, you can take the one at the root of this repository (minus the flake8 rule as legacy Toolkit applications have a lot of cleanup that needs to be done), copy it into your new repository and then commit it. Then, run `pre-commit install`. If you've committed third-party modules inside your repo, you should update the `exclude` regular expression in that file so your third-parties are not reformatted. Once you've properly set the exclusion list, it's also a good idea to run `pre-commit run --all` so that all files in the repository are reformatted.

Note that it is possible to have pre-commit [configured automatically](https://pre-commit.com/#automatically-enabling-pre-commit-on-repositories) when cloning repositories or creating new ones.

## `pytest`

`pytest` is a very popular test runner. `tk-toolchain` comes with a `pytest`-plugin that replicates the functionality found in `tests/run_tests.py` of tk-core. It removes the need to launch Toolkit unit tests using the `run_tests.sh/run_tests.bat` scripts from `tk-core` and of its test runner.

### Cheatsheet

If you are unfamiliar with pytest, here's a quick cheatsheet of things you'll want to do on a daily-basis.

-  Stop using the `self.assert*` methods from `TestCase/TankTestBase` and use `assert` when writing tests. `pytest` introspecs the code and detailled errors will show up. For example, for `assert a == b`, where a == 1 and b == 2, pytest will print out
```
>       assert a == b
E       assert 1 == 2
```
- Run a subset of the tests by typing `pytest -k something`. Any test name that matches `something` will be executed. Tests are named after the file they reside in, the class and method name. For example `tests/authentication_tests/test_auth_settings.py::DefaultsManagerTest::test_backwards_compatible`. As you can see, using `-k` you can easily run the tests of a single folder, file, class or a test.
- You can tell `pytest` to stop the execution right into the debugger where an unhandled exception is thrown by passing in `--pdb`.

### Toolkit's `pytest` plugin, `pytest_tanktest`

This is a `pytest` plugin that allows to easily run Toolkit tests written with `tk-core`'s `TankTestBase`, regardless of the repository. It does quite a few things, namely:

#### Adds the Toolkit core to the `PYTHONPATH`

The Toolkit core will be added at the front of the `PYTHONPATH`, assuming it is installed in a sibling folder to your current repository as explained [above](#pre-requisites).

#### Exposes the common folder for all your repositories

The folder in which all your repositories have been cloned will be exposed via the `SHOTGUN_REPOS_ROOT` environment variable. In the [above](#pre-requisites) example, the common folder for all the repositories is `/home/yourlogin/git-repos`.

This can be used to quickly reference any Toolkit bundle that you might require during testing. For example:

```yaml
tk-framework-qtwidgets_v2.x.x:
    location:
        type: dev
        path: $SHOTGUN_REPOS_ROOT/tk-framework-qtwidgets
tk-framework-shotgunutils_v5.x.x:
    location:
        type: dev
        path: $SHOTGUN_REPOS_ROOT/tk-framework-shotgunutils
```

This would allow your tests to run wherever the repositories have been cloned, as long as they are next to each other
on your filesystem. [Toolkit's CI/CD pipeline](https://github.com/shotgunsoftware/tk-ci-tools) lays out repositories this way.

#### Adds any Python modules for your tests into the `PYTHONPATH`

If your repository contains a folder named `tests/python`, it will be added at the front of the `PYTHONPATH`. This
allows your test modules to share common building blocks.

#### Configures a Toolkit log file for your tests

The Toolkit log for your tests will be written out in the standard Toolkit log file location under the name `tk-test.log`. Unless `SHOTGUN_HOME` [has been set](http://developer.shotgridsoftware.com/tk-core/utils.html?highlight=logmanager#sgtk.util.LocalFileStorageManager), the logs will be found under

| Platform | Location                                     |
| -------- | -------------------------------------------- |
| macOs    | `~/Library/Logs/Shotgun/tk-test.log`         |
| Windows  | `%APPDATA%\Roaming\Shotgun\Logs\tk-test.log` |
| Linux    | `~/.shotgun/logs/tk-test.log`                |

#### Provides a test engine

A bare-bones implementation of a Toolkit engine is provided and can be referenced in your configurations via the `SHOTGUN_TEST_ENGINE` environment variable. This can replace the need to use a fully-featured engine like `tk-shell` or `tk-maya` to run your tests. `sgtk.platform.qt` and `sgtk.platform.qt5` will be initialized as expected.

You can refer to this engine in the configuration file for your tests like this:

```yaml
tk-testengine:
    location:
        type: dev
        path: $SHOTGUN_TEST_ENGINE
```

#### Detects missing repositories

Each Toolkit repository can have an Azure Pipelines repository which instructs the pipeline which repositories should be cloned. `pytest_tanktest` uses that file to ensure that you have all the proper repositories cloned so that the tests can succeed.

## `tk-docs-preview`

This tool allows to build the documentation for a Toolkit bundle or the Python API repository. Just like the `pytest` plugin, it [makes assumptions](#pre-requisites) about the folder structure on disk to make it as simple as typing `tk-docs-preview` on the command line to build the documentation and get a preview in the browser.

Here's the `--help` output.

```
Usage: tk-docs-preview OPTIONS (run with --help for more options)

This tool previews sphinx documentation for a Toolkit bundle or the Shotgun
Python API. It script generates sphinx doc for a repository you have locally
on disk. This is useful for in-progress doc generation and when you want a
quick turnaround.

Options:
  -h, --help            show this help message and exit
  -v, --verbose         Enable verbose logging
  -c CORE, --core=CORE  Path to Toolkit Core. Only needed for apps, engines
                        and frameworks. Defaults to the folder next to the
                        current repository.
  -b BUNDLE, --bundle=BUNDLE
                        Path to the app/engine/fw you want to process.
                        Defaults to the current repository location.

Examples:

Shotgun API:       tk-docs-preview --bundle=/path/to/shotgun/python-api
Toolkit Core API:  tk-docs-preview --bundle=/path/to/tk-core
Toolkit Framework: tk-docs-preview --bundle=/path/to/tk-framework-xyz --core=/path/to/tk-core

For all of these examples, if your folder hierarchy is similar to

    /home/you/gitrepos/tk-core
    /home/you/gitrepos/python-api
    /home/you/gitrepos/tk-multi-toolkitapp

then the tool will find all the required folders on its own and you will only need
to type "tk-docs-preview" to preview the documentation
```

## `tk-run-app`

This tool allows you to launch apps like the Toolkit Publisher, Loader or Panel straight from the command line. Simply type `tk-run-app` from the repository of an application and the tool will launch all the registered actions. If you do not specify a context, it will use the first non-template project it finds in Shotgun server as the context.

Here's the ``--help`` output.

```
Toolkit Application Runner

Launch a Toolkit application from the command line by running this tool in any
Toolkit repository.

Usage:
    tk-run-app [--context-entity-type=<entity-type>] [--context-entity-id=<entity-id>] [--location=<location>]

Options:

    -e, --context-entity-type=<entity-type>
                       Specifies the type of the entity of the context.

    -i, --context-entity-id=<entity-id>
                       Specifies the id of the entity of the context.

    --location=<location>
                        Specifies the location where the Toolkit application is.
                        If missing, the tk-run-app assumes it is run from inside
                        the repository and launch the application at the root of
                        it.
```

Known limitations:

- Only works with applications that do not depend on DCC-specific code.
- The app can use frameworks, but they need to be compatible with the latest version of `tk-framework-qtwidgets`, `tk-framework-shotgunutils` and `tk-framework-widget`.

## `tk-config-update`

This is an internal tool that allows the Toolkit team to easily update a configuration whenever a new version of a bundle is tagged on a repository on Github. By default, the changes are not pushed back to the origin. Adding `--push-changes` will push the changes back to the origin.

```
Toolkit Configuration Update

Update the version of a bundle in a config to the specified version and pushes
it back to the source repository.

Usage:
    tk-config-update <config> <bundle> <version> [--push-changes]

Options:
    --push-changes  Pushes the changes to the repository. If not specified,
                    the remote repository is not updated.

Example:
    tk-config-update git@github.com:shotgunsoftware/tk-config-default2.git tk-core v0.19.0
```

## `tk-build-qt-resources`

This is a Python script that compiles Qt .ui and .qrc files into Python files using PySide2 compilers. The script allows you to specify the compilers directly or provide a Python environment path to locate them.

```
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
```

And then it is going to be necessary to have a 'build_resources.yml' file in each repository.
So this YAML file defines the configuration for building Qt UI and resource files using the tk-build-qt-resources script.
Each entry in the file represents a separate build configuration with the following fields:

- `ui_src`: The source directory containing the Qt .ui files.
- `ui_files`: A list of .ui file names (without extensions) to compile.
- `new_names_ui_files`: (Optional) A list of new names for the compiled .ui files (without extensions).
                      If not provided, the original names will be used.
- `res_files`: A list of .qrc resource file names (without extensions) to compile.
- `py_dest`: (Optional) The destination directory where the compiled .py files will be placed,
           (default is same directory of 'ui_src').
- `import_pattern`: (Optional) The import text pattern to replace (default is "tank.platform.qt").

Example:
```
- ui_src: path/to/ui_files
  ui_files:
    - main_window
  res_files:
    - resources
  py_dest: path/to/output
  import_pattern: custom.import.path
```

# FAQ

## When I run `tk-run-app` or `tk-docs-preview`, I get `command not found: tk-run-app`

On certain platforms, command line tools are installed in a folder that is not necessarily in your PATH. Find where your python interpreter installs command line tools on your platform and add that location to your path. Another option is to run the tools using `python -m <module-name>`. For example:

- `tk-run-app` : `python -m tk_toolchain.cmd_line_tools.tk_run_app`
- `tk-docs-preview` : `python -m tk_toolchain.cmd_line_tools.tk_docs_generation`
