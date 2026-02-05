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

####################################################################################
# imports and general setup

import os
import logging
import webbrowser
import optparse
import sys

from .sphinx_processor import SphinxProcessor

from tk_toolchain.repo import Repository
from tk_toolchain import util

# set up logging channel for this script
log = logging.getLogger("sgtk.sphinx")


class OptionParserLineBreakingEpilog(optparse.OptionParser):
    """
    Subclassed version of the option parser that doesn't
    swallow white space in the epilog
    """

    def format_epilog(self, formatter):
        return self.epilog


def preview_docs(
    core_path,
    bundle_path,
    is_build_only,
    warnings_as_errors=True,
    additional_paths=None,
):
    """
    Generate doc preview in a temp folder and show it in
    a web browser.

    :param core_path: Path to toolkit core
    :param bundle_path: Path to app/engine/fw to document
    :param additional_paths: Additional file paths to prepend to the PYTHONPATH and sys.path, for
        sphinx to generate the docs.
    """

    log.info("Starting preview run for %s" % bundle_path)
    sphinx_processor = SphinxProcessor(core_path, bundle_path, log, additional_paths)

    # Project Name:
    # assume the name of the folder is the name of the sphinx project
    # e.g. /path/to/git/tk-my-app --> 'tk-my-app'
    #
    # NOTE! This is only handled this way during the preview phase.
    # when you run the proper publishing script, where the git tag/branch
    # is well known, the documentation name will be pulled strictly from
    # the repository data.
    #
    # But here - in preview mode - the itention is to keep things as flexible
    # as possible, not even assuming the existence of a git repo at this point
    # so we pull the *temporary preview name* for the docs from the folder
    # name.
    #
    doc_name = os.path.basename(bundle_path)

    log.info(
        "Note: In preview mode, a placeholder documentation title will be "
        "extracted from the path where the content is located. "
        "Later on when you release the documentation using "
        "the release script, the proper github details will be extracted."
    )

    # build docs
    location = sphinx_processor.build_docs(doc_name, "vX.Y.Z", warnings_as_errors)

    if not is_build_only:
        # show in browser
        webbrowser.open_new("file://%s" % os.path.join(location, "index.html"))

    log.info("Doc generation done.")


####################################################################################
# script entry point


def main(arguments=None):
    arguments = arguments or sys.argv

    log.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    formatter = logging.Formatter("%(levelname)s %(message)s")
    ch.setFormatter(formatter)
    log.addHandler(ch)

    exit_code = 1
    try:
        usage = "%prog OPTIONS (run with --help for more options)"

        desc = (
            "This tool previews sphinx documentation for a Toolkit bundle or the "
            "Shotgun Python API. It generates a sphinx doc for a repository you "
            "have locally on disk. This is useful for in-progress doc generation and "
            "when you want a quick turnaround."
        )

        epilog = """
Examples:

Shotgun API:       tk-docs-preview --bundle=/path/to/shotgun/python-api
Toolkit Core API:  tk-docs-preview --bundle=/path/to/tk-core
Toolkit Framework: tk-docs-preview --bundle=/path/to/tk-framework-xyz --core=/path/to/tk-core

For all of these examples, if your folder hierarchy is similar to

    /home/you/gitrepos/tk-core
    /home/you/gitrepos/python-api
    /home/you/gitrepos/tk-multi-toolkitapp

then the tool will find all the required folders on it's own and you will only need
to type "tk-docs-preview" to preview the documentation.
"""

        parser = OptionParserLineBreakingEpilog(
            usage=usage, description=desc, epilog=epilog
        )

        parser.add_option(
            "-v",
            "--verbose",
            default=False,
            action="store_true",
            help="Enable verbose logging",
        )

        parser.add_option(
            "-c",
            "--core",
            default=None,
            help=(
                "Path to Toolkit Core. Only needed for apps, engines and frameworks. Defaults to the folder "
                "next to the current repository."
            ),
        )

        parser.add_option(
            "-b",
            "--bundle",
            default=None,
            help="Path to the app/engine/fw you want to process. Defaults to the current repository location.",
        )

        parser.add_option(
            "--build-only",
            default=False,
            action="store_true",
            help="Build the documentation but do not open a browser to display it.",
        )

        parser.add_option(
            "--additional-paths",
            default=None,
            help=(
                "Additional file paths to prepend to the PYTHONPATH and sys.path before Sphinx generates "
                "the docs. Specify multiple file paths by separating with semi-colon ';'."
            ),
        )

        # parse cmd line
        options, _ = parser.parse_args(arguments)

        # Unless bundle is overridden, we'll assume the current repo root is the bundle
        try:
            repo = Repository(util.expand_path(options.bundle or os.getcwd()))
        except RuntimeError:
            log.info("This does not appear to be a known repository type.")
            return 0

        if not os.path.exists(os.path.join(repo.root, "docs")):
            log.info("No documentation was found.")
            return 0

        # Make sure Qt is available if we're dealing with Toolkit repos.
        if not repo.is_python_api() and not repo.is_sg_jira_bridge():
            try:
                import PySide2  # noqa
            except ImportError:
                try:
                    import PySide6  # noqa
                except ImportError:
                    log.error(
                        "PySide2, or PySide6 are required to build the documentation."
                    )
                    return 1
        # If the specified the core path, we'll use it.
        if options.core:
            core_path = util.expand_path(options.core)
        elif any(
            # The Python API, Jira Bridge, tk-toolchain and tk-core do not
            # require the core path to be set.
            (
                repo.is_python_api(),
                repo.is_tk_toolchain(),
                repo.is_tk_core(),
                repo.is_sg_jira_bridge(),
            )
        ):
            core_path = None
        # The user didn't specify the core location, so we'll have to guess it.
        else:
            core_path = os.path.join(repo.parent, "tk-core")

        if options.verbose:
            log.setLevel(logging.DEBUG)
            log.debug("Enabling verbose logging.")

        # Get the additional paths from the command line options. Split the string by ';' for multiple paths.
        if options.additional_paths:
            additional_paths = options.additional_paths.split(";")
        else:
            additional_paths = None

        # In case we're dealing with tk-core documentation, we need to add the new bootstrap hook location
        # as additional path to be able to generate the documentation
        if repo.is_tk_core():
            additional_tk_core_path = os.path.join(
                repo.root, "python", "tank", "bootstrap", "hooks"
            )
            if os.path.exists(additional_tk_core_path):
                additional_paths = (
                    [additional_tk_core_path]
                    if not additional_paths
                    else additional_paths.append(additional_tk_core_path)
                )

        preview_docs(
            core_path,
            repo.root,
            options.build_only,
            additional_paths=additional_paths,
        )
        exit_code = 0
    except Exception as e:
        if options.verbose:
            log.exception("An exception was raised: %s" % e)
        else:
            log.error("An exception was raised: %s" % e)

    log.info("Exiting with code %d. Sayonara." % exit_code)
    return exit_code
