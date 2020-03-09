# Copyright (c) 2017 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import json

from sgtk.platform import SoftwareLauncher, SoftwareVersion, LaunchInformation


class TestLauncher(SoftwareLauncher):

    def scan_software(self):
        """
        For each software executable that was found, get the software products for it.

        :returns: List of :class:`SoftwareVersion`.
        """

        # A list of software scan results can be provided via the SHOTGUN_SCAN_SOFTWARE_LIST env var
        # as a serialized json string in the following format
        # [
        #     [
        #         "2050", # version
        #         "Software Name",
        #         "path/to/executable",
        #         "path/to/icon", # optional can be empty string
        #         ["arg1", "arg2"], # args, can be an empty list
        #     ]
        # ]

        software_list = []

        serialized_software_list = os.environ.get("SHOTGUN_SCAN_SOFTWARE_LIST")
        imported_software_list = json.loads(serialized_software_list)
        if imported_software_list:
            for scanned_software in imported_software_list:
                sw = SoftwareVersion(*scanned_software)
                software_list.append(sw)
        else:
            # No scanned software was provided to so provide a single default software.
            software_list = [SoftwareVersion(
                "2020",
                "Test Software",
                "path/to/software_2020.app",
                "",
                []
            )]
        return software_list

    @property
    def minimum_supported_version(self):
        """
        Minimum supported version by this launcher.
        """
        return "7.0v10"

    def prepare_launch(self, exec_path, args, file_to_open=None):
        """
        """

        # Add std context and site info to the env.
        required_env = self.get_standard_plugin_environment()

        return LaunchInformation(exec_path, args, required_env)

