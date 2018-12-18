# Copyright (c) 2018 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import requests


def get_pull_request_base_commit(repo_slug, pull_request_id):
    """
    Retrieves the base of a pull request, i.e. what the Github diff is made
    against for a given repo's pull request.
    """
    return requests.get(
        "https://api.github.com/repos/{}/pulls/{}".format(
            repo_slug, pull_request_id
        )
    ).json()["base"]["sha"]
