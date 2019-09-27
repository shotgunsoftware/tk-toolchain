# Toolkit Build tools

The Toolkit Build tools will help developers of Toolkit-based applications in their day to day development tasks. It is meant
to be installed as a pip package and can be used both locally or on a continuous integration service to validate their code
and documentation.

# What can it do?

Here are the tools that the library offers:

`pytest_tk_build`: This is a `pytest` plugin that allows to easily run Toolkit tests written with `tk-core`'s `TankTestBase`
regardless of the repository. It also provides a collection of environment variables and a test engine to help application
developers to write tests.

`tk_docs_preview`: This tools allows to preview the documentation in the `docs` folder of a Toolkit application.

# Pre-requisites

The tool assumes that all your Toolkit-based repositories are in the same folder. For example:

```
/home/yourlogin/git-repos/tk-core
/home/yourlogin/git-repos/tk-multi-publish2
/home/yourlogin/git-repos/tk-framework-shotgunutils
...
```

This allows the tool to quickly find other repositories it might need to run the tests or generate the documentation.

# How can I install these tools?

Simply type `pip install https://github.com/shotgunsoftware/tk-build.git` and all the required modules will be installed
for you.

Then, type `pytest` to run the unit tests inside a Toolkit repository or `tk-docs-preview` to preview the documentation in the
docs folder.

# `pytest_tk_build`

This `pytest` plugins offers a collection of services that will help a Toolkit developer to write tests and run them with `pytest`.
It removes the need for custom shell scripts that use the `run_tests.sh|bat` scripts from tk-core and the use of the `run_tests.py`
test runner.

The plugin will take care of the following at `pytest` startup:

- Add `tk-core` to the `PYTHONPATH` (this assumes that there's `tk-core` folder right next to your repo, as explained [above](#pre-requisites))
- Set `TK_TEST_FIXTURES`, which is used by `TankTestBase` to find test data that can be used for initializing `Mockgun` or setting
up tests projects using `TankTestBase.setup_fixtures`. For more information about `TankTestBase`, you can visit our documentation
[here](https://github.com/shotgunsoftware/tk-core/blob/master/tests/README.md).
