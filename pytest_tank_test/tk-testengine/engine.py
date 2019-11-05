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

import sgtk


class TestEngine(sgtk.platform.Engine):
    """
    Test engine.

    The engine will initialize a QApplication if possible right before
    applications start registering themselves so it looks as if they
    are running within a GUI environment.
    """

    def pre_app_init(self):
        try:
            q_app = sgtk.platform.qt.QtGui.QApplication.instance()
            self._q_app = q_app or sgtk.platform.qt.QtGui.QApplication([])
        except Exception:
            # This will fail if Qt is not available.
            self._q_app = None

        if self._q_app:
            self._initialize_dark_look_and_feel()

    @property
    def q_app(self):
        """
        The QtGui.QApplication instance, if available.
        """
        return self._q_app

    def _emit_log_message(self, handler, record):
        """
        Print any log message to the console.
        """
        print(handler.format(record))
