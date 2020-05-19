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

import pytest
from mock import Mock


from tk_toolchain.authentication import _get_toolkit_user


@pytest.fixture
def sg_auth_mock():
    args = {}
    # Create a mock object that returns all parameters passed to the mocked function and
    # ensures only a small number of methods can be called on the mock.
    for method in "create_session_user", "create_script_user", "get_user":
        args[method] = Mock(spec_list=[])
        args[method].side_effect = lambda *args, **kwargs: set(
            list(args) + list(kwargs.values())
        )
    return Mock(spec_list=list(args.keys()), **args)


def test_user_based_auth(sg_auth_mock):
    """
    Test used based auth.
    """
    env = {
        "TK_TOOLCHAIN_HOST": "https://a.b.com",
        "TK_TOOLCHAIN_USER_LOGIN": "elvis",
        "TK_TOOLCHAIN_USER_PASSWORD": "hailToTheKing",
    }
    result = _get_toolkit_user(sg_auth_mock, env)
    assert sg_auth_mock.create_session_user.called
    assert result == set(env.values())


def test_script_based_auth(sg_auth_mock):
    """
    Test script based auth.
    """
    env = {
        "TK_TOOLCHAIN_HOST": "https://a.b.com",
        "TK_TOOLCHAIN_SCRIPT_NAME": "automation",
        "TK_TOOLCHAIN_SCRIPT_KEY": "!$3,asdas$dfadf*(0",
    }
    result = _get_toolkit_user(sg_auth_mock, env)
    assert sg_auth_mock.create_script_user.called
    assert result == set(env.values())


def test_no_user_specified_auth(sg_auth_mock):
    """
    Test manual auth.
    """
    _get_toolkit_user(sg_auth_mock, {})
    assert sg_auth_mock.get_user.called
