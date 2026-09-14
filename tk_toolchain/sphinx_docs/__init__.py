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

"""
Library for generating Sphinx documentation for Toolkit bundles. Used both by
the tk-docs-preview command line tool and by tk-internal's release script.
"""

import os
import logging
import webbrowser

from .sphinx_processor import SphinxProcessor

from tk_toolchain.repo import Repository

# set up logging channel for this script
log = logging.getLogger("sgtk.sphinx")


def preview_docs(
    core_path,
    bundle_path,
    is_build_only,
    warnings_as_errors=True,
    additional_paths=None,
    doc_name=None,
    version=None,
):
    """
    Generate sphinx docs for a bundle, making sure Qt is available first.

    :param core_path: Path to toolkit core
    :param bundle_path: Path to app/engine/fw to document
    :param additional_paths: Additional file paths to prepend to the PYTHONPATH and sys.path, for
        sphinx to generate the docs.
    :param doc_name: Name to give the documentation. Defaults to the bundle folder's name, which
        is only accurate during local preview.
    :param version: Version to associate with the documentation. Defaults to a placeholder, which
        is only accurate during local preview.

    :returns: Path to the built docs.

    :raises RuntimeError: If the bundle requires Qt to build its docs and Qt isn't available.
    """
    repo = Repository(bundle_path)
    if not repo.is_python_api() and not repo.is_sg_jira_bridge():
        try:
            import PySide2  # noqa
        except ImportError:
            try:
                import PySide6  # noqa
            except ImportError:
                raise RuntimeError(
                    "PySide2, or PySide6 are required to build the documentation."
                )

    log.info("Starting preview run for %s" % bundle_path)
    sphinx_processor = SphinxProcessor(core_path, bundle_path, log, additional_paths)

    if doc_name is None:
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
    location = sphinx_processor.build_docs(
        doc_name, version or "vX.Y.Z", warnings_as_errors
    )

    if not is_build_only:
        # show in browser
        webbrowser.open_new("file://%s" % os.path.join(location, "index.html"))

    log.info("Doc generation done.")

    return location
