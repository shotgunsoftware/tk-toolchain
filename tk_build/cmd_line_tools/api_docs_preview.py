#!/usr/bin/env python
"""
Copyright (c) 2015 Shotgun Software, Inc
----------------------------------------------------
"""

####################################################################################
# imports and general setup

import os
import logging
import webbrowser
import optparse
import sys

# PREPEND python location to pythonpath
python_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "python"))
sys.path.insert(0, python_path)

from .sphinx_processor import SphinxProcessor

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

    log.info("Note: In preview mode, a placeholder documentation title will be "
             "extracted from the path where the content is located. "
             "Later on when you release the documentation using "
             "the release script, the proper github details will be extracted.")

    # build docs
    location = sphinx_processor.build_docs(doc_name, "vX.Y.Z")

    # show in browser
    webbrowser.open_new("file://%s" % os.path.join(location, "index.html"))

    log.info("Doc generation done.")

####################################################################################
# script entry point


def main():

    usage = "%prog OPTIONS (run with --help for more options)"

    desc  = "Preview sphinx documentation for an app/engine/framework. "
    desc += "This script generates sphinx doc for an app/engine/fw you have "
    desc += "locally on disk somewhere. This is useful for in-progress doc "
    desc += "generation and when you want a quick turnaround. When you "
    desc += "are ready to release your docs, use the api_docs_to_github script. "
    desc += "For info, see https://wiki.autodesk.com/display/SHOT/Managing+API+Reference+Documentation"

    epilog = """
Examples:

Shotgun API:       python api_docs_preview.py --bundle=/path/to/shotgun/python-api
Toolkit Core API:  python api_docs_preview.py --bundle=/path/to/tk-core
Toolkit Framework: python api_docs_preview.py --bundle=/path/to/tk-framework-xyz --core=/path/to/tk-core
"""

    parser = OptionParserLineBreakingEpilog(usage=usage, description=desc, epilog=epilog)

    parser.add_option("-v", "--verbose",
                      default=False,
                      action="store_true",
                      help="Enable verbose logging"
                      )

    parser.add_option("-c", "--core",
                      default=None,
                      help="Path to Toolkit Core. Only needed for apps, engines and frameworks")

    parser.add_option("-b", "--bundle",
                      help="Path to the app/engine/fw you want to process.")

    # parse cmd line
    (options, _) = parser.parse_args()

    # check for missing params
    if not options.bundle:
        parser.error("Missing bundle parameter.")
        return

    if options.verbose:
        log.setLevel(logging.DEBUG)
        log.debug("Enabling verbose logging.")

    core_path = os.path.expandvars(os.path.expanduser(options.core)) if options.core else None
    bundle_path = os.path.expandvars(os.path.expanduser(options.bundle)) if options.bundle else None

    preview_docs(core_path, bundle_path)

if __name__ == "__main__":
    log.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    formatter = logging.Formatter("%(levelname)s %(message)s")
    ch.setFormatter(formatter)
    log.addHandler(ch)

    exit_code = 1
    try:
        main()
        exit_code = 0
    except Exception, e:
        log.exception("An exception was raised: %s" % e)

    log.info("Exiting with code %d. Sayonara." % exit_code)
    sys.exit(exit_code)