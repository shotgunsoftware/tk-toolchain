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
from tk_toolchain import ci

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


def preview_docs(core_path, bundle_path):
    """
    Generate doc preview in a temp folder and show it in
    a web browser.

    :param core_path: Path to toolkit core
    :param bundle_path: Path to app/engine/fw to document
    """

    log.info("Starting preview run for %s" % bundle_path)
    sphinx_processor = SphinxProcessor(core_path, bundle_path, log)

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
    location = sphinx_processor.build_docs(doc_name, "vX.Y.Z")

    if not ci.is_in_ci_environment():
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
            "Shotgun Python API. It script generates sphinx doc for a repository you "
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

        # parse cmd line
        (options, _) = parser.parse_args(arguments)

        # Unless bundle is overridden, we'll assume the current repo root is the bundle
        repo = Repository(util.expand_path(options.bundle or os.getcwd()))

        # Make sure Qt is available if we're dealing with Toolkit repos.
        if not repo.is_python_api():
            try:
                import PySide  # noqa
            except ImportError:
                try:
                    import PySide2
                except ImportError:
                    log.error(
                        "PySide or PySide2 are required to build the documentation."
                    )
                    return

        # If the specified the core path, we'll use it.
        if options.core:
            core_path = util.expand_path(options.core)
        # The Python API, tk-toolchain and tk-core do not require the core path to be set.
        elif repo.is_python_api() or repo.is_tk_toolchain() or repo.is_tk_core():
            core_path = None
        # The user didn't specify the core location, so we'll have to guess it.
        else:
            core_path = os.path.join(repo.parent, "tk-core")

        if options.verbose:
            log.setLevel(logging.DEBUG)
            log.debug("Enabling verbose logging.")

        preview_docs(core_path, repo.root)
        exit_code = 0
    except Exception as e:
        if options.verbose:
            log.exception("An exception was raised: %s" % e)
        else:
            log.error("An exception was raised: %s" % e)

    log.info("Exiting with code %d. Sayonara." % exit_code)
    return exit_code
