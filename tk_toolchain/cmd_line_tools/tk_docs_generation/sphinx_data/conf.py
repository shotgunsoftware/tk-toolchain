# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.
#
# S P H I N X    C O N F I G U R A T I O N    F I L E
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

from __future__ import print_function
import logging
import sys


def setup_toolkit():
    try:
        # run toolkit init. The doc generation scripts bootstrap script have already
        # set the PYTHONPATH so both the app we are documenting and core should be
        # available at this point.
        import tank
    except:
        # not every documentable environment needs sgtk
        print(
            "WARNING: Unable to import Toolkit. This is fine if you're only "
            "building the Python API documentation."
        )
        return

    try:
        # components also use PySide, so make sure  we have this loaded up correctly
        # before starting auto-doc.
        from tank.util.qt_importer import QtImporter

        importer = QtImporter()

        tank.platform.qt.QtCore = importer.QtCore
        tank.platform.qt.QtGui = importer.QtGui
    except:
        print("WARNING: PySide was not found in the current environment.")
        pass

    # some frameworks import other frameworks and this means that they have
    # an import_framework method call that executes right at load time.
    # this method requires a running sgtk platform and will prevent
    # sphinx to run its introspection, so we need to replace these import
    # methods with proxy

    class ModuleImportProxy(object):
        """
        Proxy class that returns None for any attribute request.
        This so that the code that is being documented can
        execute this type of code at import time without
        erroring out:

        version_label = sgtk.platform.current_bundle().import_module("version_label")
        VersionLabel = version_label.VersionLabel
        """

        def __getattr__(self, name):
            return object

    class BundleProxy(object):
        """
        Proxy object representing a tank bundle object.
        This is primarily so we can implement a proxy wrapper for
        the import_module method and use that to return a module
        proxy object above.
        """

        def import_module(*args, **kwargs):
            return ModuleImportProxy()

    def make_module_proxy(*args, **kwargs):
        """
        Override method that returns a module proxy object
        """
        return ModuleImportProxy()

    def make_bundle_proxy(*args, **kwargs):
        """
        Override method that returns a bundle proxy object
        """
        return BundleProxy()

    # Monkey patch Toolkit so Toolkit bundles can be loaded for documentation
    # purpose.
    try:
        import sys

        sys.setrecursionlimit(1500)

        # make sure we patch our proxy methods with doc strings
        # otherwise we can never generate documentation for them :-)
        from tank.platform import import_framework as real_import_framework
        from tank.platform import current_bundle as real_current_bundle
        from tank import get_hook_baseclass as real_get_hook_baseclass

        make_module_proxy.__doc__ = real_import_framework.__doc__
        make_bundle_proxy.__doc__ = real_current_bundle.__doc__

        # now patch toolkit
        tank.platform.import_framework = make_module_proxy
        tank.platform.import_framework = make_module_proxy

        tank.platform.current_bundle = make_bundle_proxy
        tank.platform.current_bundle = make_bundle_proxy

        tank.platform.get_logger = lambda x: logging.getLogger(x)

        # patch hook baseclass to return Hook (it doesn't have a default value)
        get_hook_baseclass_proxy = lambda: tank.Hook
        get_hook_baseclass_proxy.__doc__ = real_get_hook_baseclass.__doc__

        tank.get_hook_baseclass = get_hook_baseclass_proxy

    except Exception:
        import traceback

        traceback.print_exc()


setup_toolkit()


################################
# Python API 3 specific options


def remove_module_docstring(app, what, name, obj, options, lines):
    """We remove the copyright from the Shotgun module because it's annoying"""
    if what == "module" and name == "shotgun_api3.shotgun":
        del lines[:]


def setup(app):
    app.connect("autodoc-process-docstring", remove_module_docstring)


########################
# General configuration

# If your documentation needs a minimal Sphinx version, state it here.
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.graphviz",
    "sphinx.ext.intersphinx",
]

# FIXME: Toolkit API does not rely on this plugin. Adding it generates errors.
# The Python API on the other hand does and we don't have time to fix the doc before
# the rebrand, so add the plugin for the Python API and call it a day.
is_python_api = False
for arg in sys.argv:
    if "python-api" in arg:
        extensions.append("sphinx.ext.autosectionlabel")
        break


# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
# source_suffix = ['.rst', '.md']
source_suffix = ".rst"

# The encoding of source files.
# source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = "index"

# General information about the project.
# project = u'Specify this via command line'
from datetime import date

copyright = "%s, Autodesk" % date.today().year
author = "Autodesk"

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = "vX.Y.Z"
# The full version, including alpha/beta/rc tags.
release = "vX.Y.Z"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
# today = ''
# Else, today_fmt is used as the format for a strftime call.
# today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = []

# The reST default role (used for this markup: `text`) to use for all
# documents.
# default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
# add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
# add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
# show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "default"

# A list of ignored prefixes for module index sorting.
# modindex_common_prefix = []

# If true, keep warnings as "system message" paragraphs in the built documents.
# keep_warnings = False

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "sphinx_rtd_theme"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {"display_version": False}

# Add any paths that contain custom themes here, relative to this directory.
# html_theme_path = []

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
# html_title = None

# A shorter title for the navigation bar.  Default is the same as html_title.
# html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
# html_logo = None

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
html_favicon = "favicon.ico"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Add any extra paths that contain custom files (such as robots.txt or
# .htaccess) here, relative to this directory. These files are copied
# directly to the root of the documentation.
# html_extra_path = []

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
# html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
# html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
# html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
# html_additional_pages = {}

# If false, no module index is generated.
html_domain_indices = False

# If false, no index is generated.
# html_use_index = True

# If true, the index is split into individual pages for each letter.
# html_split_index = False

# If true, links to the reST sources are added to the pages.
html_show_sourcelink = False

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
html_show_sphinx = False

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
# html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
# html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
# html_file_suffix = None

# Language to be used for generating the HTML full-text search index.
# Sphinx supports the following languages:
#   'da', 'de', 'en', 'es', 'fi', 'fr', 'hu', 'it', 'ja'
#   'nl', 'no', 'pt', 'ro', 'ru', 'sv', 'tr'
# html_search_language = 'en'

# A dictionary with options for the search language support, empty by default.
# Now only 'ja' uses this config value
# html_search_options = {'type': 'default'}

# The name of a javascript file (relative to the configuration directory) that
# implements a search results scorer. If empty, the default will be used.
# html_search_scorer = 'scorer.js'

###################################################################################################################
#
# toolkit specific modifications and additions
#
###################################################################################################################

# this tells sphinx to include both the doc string from __init__
# and from the class doc string when creating the doc chunk for a
# class. Without this set, the constructor parameters cannot easily be
# documented.
autoclass_content = "both"

# Output file base name for HTML help builder.
htmlhelp_basename = "tkdoc"

# external references. This allows for proper cross referencing between bundles
# and extrnal libs
intersphinx_mapping = {
    "python": ("https://docs.python.org/3.9", None),
    "PySide": ("http://pyside.github.io/docs/pyside/", None),
    "PySide2": ("https://doc.qt.io/qtforpython-5", None),
    "PySide6": ("https://doc.qt.io/qtforpython-6", None),
    "sgtk": ("http://developers.shotgridsoftware.com/tk-core/", None),
    "tk-framework-qtwidgets": (
        "https://developers.shotgridsoftware.com/tk-framework-qtwidgets/",
        None,
    ),
    "tk-framework-shotgunutils": (
        "https://developers.shotgridsoftware.com/tk-framework-shotgunutils/",
        None,
    ),
    "shotgun-api3": ("https://developers.shotgridsoftware.com/python-api", None),
}

autodoc_member_order = "bysource"

suppress_warnings = ["image.nonlocal_uri"]
