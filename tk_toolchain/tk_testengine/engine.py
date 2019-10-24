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

from sgtk.platform import Engine


class TestEngine(Engine):
    """
    Simple test engines that will just run any app you throw at it.
    """

    def pre_app_init(self):
        """
        Sets the dark theme
        """
        self._initialize_dark_look_and_feel()
        super(TestEngine, self).pre_app_init()

    def _emit_log_message(self, handler, record):
        print(handler.format(record))
