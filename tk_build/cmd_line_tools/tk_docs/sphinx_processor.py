"""

Copyright (c) 2015 Shotgun Software, Inc
----------------------------------------------------

Contains methods for generating sphinx based documentation

"""

import os
import sys
import shutil
import tempfile


def execute_command(log, command, expected_code=0):
    """
    Helper. executes shell command and raises exception
    if return code is nonzero
    """
    if log:
        log.info("[CMD: %s]" % command)
    ret = os.system(command)
    if ret != expected_code:
        raise Exception("Command returned Error code %s - aborting!" % ret)
    if log:
        log.debug("Command %s executed successfully." % command)


class SphinxProcessor(object):
    """
    Class that wraps sphinx doc generation
    """

    def __init__(self, core_path, path, log):
        """
        :param core_path: Path to tk-core. If None, the core API will
                          not be added to the pythonpath.
        :param path: Path to the app/engine/fw to document
        :param log: Logger
        """
        self._log = log
        self._path = path

        self._log.debug("Starting Sphinx processor for %s..." % path)

        self._docs_path = os.path.join(path, "docs")

        if not os.path.exists(self._docs_path):
            raise Exception("Cannot find a docs folder in %s!" % path)

        # now add stuff to pythonpath
        # note that we are adding it to both sys.path and the
        # PYTHONPATH so that it gets picked up by the doc gen script
        # later on.

        # add core API
        if core_path:
            self._add_to_pythonpath(os.path.join(core_path, "python"))

        # add main bundle location
        self._add_to_pythonpath(path)

        # Add python location for the hooks.
        self._add_to_pythonpath(os.path.join(path, "hooks"))

        # and python location for bundle
        self._add_to_pythonpath(os.path.join(path, "python"))

        # check that Sphinx and PySide are available
        if core_path:
            try:
                import sgtk # noqa
            except ImportError:
                raise Exception("Cannot import sgtk. Please add to pythonpath")

        # make a temp folder for building docs
        self._sphinx_build_dir = os.path.join(tempfile.gettempdir(), "sphinx-build", os.path.basename(path))
        self._log.debug("Sphinx will build into %s..." % self._sphinx_build_dir)

        # get a path to conf.py
        this_folder = os.path.abspath(os.path.dirname(__file__))
        self._sphinx_conf_py_location = os.path.join(this_folder, "sphinx_data")
        self._log.debug("Sphinx will use configuration from %s..." % self._sphinx_conf_py_location)

    def _add_to_pythonpath(self, path):
        """
        Prepends to PYTHONPATH and sys.path

        :param path: The path to add
        """
        pythonpath = os.environ.get("PYTHONPATH", "").split(os.path.pathsep)
        path = os.path.expanduser(os.path.expandvars(path))
        pythonpath.insert(0, path)
        sys.path.insert(0, path)
        self._log.debug("Added to PYTHONPATH: %s" % path)
        os.environ["PYTHONPATH"] = os.path.pathsep.join(pythonpath)

    def build_docs(self, name, version):
        """
        Generate sphinx docs

        :param name: The name to give to the documentation
        :param version: The version number to associate with the documentation
        :returns: Path to the built docs
        """
        self._log.debug("Building docs with name %s and version %s" % (name, version))

        # run build command
        # Use double quotes to make sure it works on Windows and Unix.
        cmd = "sphinx-build -c \"%s\" -W -D project=\"%s\" -D release=\"%s\" -D version=\"%s\" \"%s\" \"%s\"" % (
            self._sphinx_conf_py_location,
            name,
            version,
            version,
            self._docs_path,
            self._sphinx_build_dir
        )

        execute_command(self._log, cmd)

        # make sure there is a .nojekyll file in the github repo, otherwise
        # folders beginning with an _ will be ignored
        no_jekyll = os.path.join(self._sphinx_build_dir, ".nojekyll")
        execute_command(self._log, "touch '%s'" % no_jekyll)

        return self._sphinx_build_dir

    def copy_docs(self, log, src, dst):
        """
        Alternative implementation to shutil.copytree
        Copies recursively with very open permissions.
        Creates folders if they don't already exist.

        :param src: Source path
        :param dst: Destination path
        """
        if not os.path.exists(dst):
            log.debug("mkdir 0777 %s" % dst)
            os.mkdir(dst, 0777)

        names = os.listdir(src)
        for name in names:

            srcname = os.path.join(src, name)
            dstname = os.path.join(dst, name)

            try:
                if os.path.isdir(srcname):
                    self.copy_docs(log, srcname, dstname)
                else:
                    shutil.copy(srcname, dstname)
                    log.debug("Copy %s -> %s" % (srcname, dstname))
            except Exception, e:
                log.error("Can't copy %s to %s: %s" % (srcname, dstname, e))
