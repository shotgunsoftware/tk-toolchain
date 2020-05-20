# -*- coding: utf-8 -*-
# Copyright (c) 2020 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os


def _get_toolkit_user(sg_auth, environment):
    """
    Retrieves the Toolkit user using the passed in authenticator and
    environment.
    """

    host = environment.get("TK_TOOLCHAIN_HOST")
    script_name = environment.get("TK_TOOLCHAIN_SCRIPT_NAME")
    script_key = environment.get("TK_TOOLCHAIN_SCRIPT_KEY")
    login = environment.get("TK_TOOLCHAIN_USER_LOGIN")
    password = environment.get("TK_TOOLCHAIN_USER_PASSWORD")

    # If all the variables were set, we can authenticate.
    if host and login and password:
        print("Authenticating from environment variables.")
        return sg_auth.create_session_user(login, password=password, host=host)
    if host and script_name and script_key:
        print("Authenticating from environment variables.")
        return sg_auth.create_script_user(script_name, script_key, host=host)
    # If one of those values has been set.
    elif (host or login or password or script_name or script_key) is not None:
        # Something was set, but not everything.
        # Do not print the values, as this can be used in CI.
        print(
            "Not all authentication environment variables were set. "
            "Falling back to interactive authentication.\n"
            "TK_TOOLCHAIN_HOST: {0}\n"
            "TK_TOOLCHAIN_USER_LOGIN: {1}\n"
            "TK_TOOLCHAIN_USER_PASSWORD: {2}\n"
            "TK_TOOLCHAIN_SCRIPT_NAME: {3}\n"
            "TK_TOOLCHAIN_SCRIPT_KEY: {4}\n".format(
                "set" if host else "unset",
                "set" if login else "unset",
                "set" if password else "unset",
                "set" if script_name else "unset",
                "set" if script_key else "unset",
            )
        )

    return sg_auth.get_user()


def get_toolkit_user():
    """
    Authenticate with a Shotgun site.

    If SHOTGUN_HOST, SHOTGUN_USER_LOGIN and SHOGUN_USER_PASSWORD
    or SHOTGUN_HOST, SHOTGUN_SCRIPT_NAME and SHOTGUN_SCRIPT_KEY
    are set, then they will be used for authentication. If not,
    the user will be prompted for their credentials if they
    are not already logged into Shotgun.

    User based authentication has precedence over script based
    authentication.

    :returns: A Shotgun user.
    :rtype: sgtk.authentication.ShotgunUser
    """

    # Lazy loading as Toolkit might not be available yet.
    from sgtk.authentication import ShotgunAuthenticator

    sg_auth = ShotgunAuthenticator()

    return _get_toolkit_user(sg_auth, os.environ)
