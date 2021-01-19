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

from tk_toolchain.testing import create_unique_name
from tk_toolchain.authentication import get_toolkit_user


def test_create_project(tk_test_shotgun, tk_test_create_project):
    """
    Ensure the project gets created successfully.
    """
    # Get project info
    project_name = create_unique_name("Toolkit UI Automation")
    filters = [["name", "is", project_name]]
    existed_project = tk_test_shotgun.find_one("Project", filters)

    # Get current project info
    current_project = tk_test_create_project

    # Make sure both file has the same id.
    assert existed_project["id"] == current_project["id"]


def test_credentials(tk_test_shotgun):
    """
    Ensure getting credentials
    """
    # Get credentials from the fixture and fin local storage with it
    fixture_credentials = tk_test_shotgun

    # Use credentials from fixture to get storage info
    storage_name = create_unique_name("Toolkit UI Automation")
    local_storage1 = fixture_credentials.find_one(
        "LocalStorage", [["code", "is", storage_name]], ["code"]
    )

    # Getting credentials from TK_TOOLCHAIN
    tk_toolchain_crendentials = get_toolkit_user().create_sg_connection()

    # Use credentials from TK_TOOLCHAIN to get storage info
    local_storage2 = tk_toolchain_crendentials.find_one(
        "LocalStorage", [["code", "is", storage_name]], ["code"]
    )

    # Make sure both storage info are identical.
    assert local_storage1 == local_storage2


def test_current_user(tk_test_shotgun, tk_test_current_user):
    """
    Ensure getting current_user
    """
    # Getting current user
    user = get_toolkit_user()
    username = tk_test_shotgun.find_one(
        "HumanUser", [["login", "is", str(user)]], ["name"]
    )

    # Getting current user with tk_test_current_user fixture
    current_user = tk_test_current_user

    # Make sure both user are identical.
    assert username == current_user


def test_create_entities(
    tk_test_create_project,
    tk_test_shotgun,
    tk_test_current_user,
    tk_test_create_entities,
):
    """
    Ensure getting current_user
    """
    # Getting task entity from create entities fixture
    task_entity_fixture = tk_test_create_entities[0]

    # Getting asset entity from create entities fixture
    publishedFile_entity_fixture = tk_test_create_entities[1]

    # Getting version entity from create entities fixture
    version_entity_fixture = tk_test_create_entities[2]

    # Getting task entity
    filters = [
        ["project", "is", tk_test_create_project],
        ["entity.Asset.code", "is", "AssetAutomation"],
        ["step.Step.code", "is", "model"],
    ]
    fields = ["sg_status_list"]
    task_entity = tk_test_shotgun.find_one("Task", filters, fields)

    # Getting publishedFile entity
    filters = [
        ["project", "is", tk_test_create_project],
        ["code", "is", "sven.png"],
    ]
    publishedFile_entity = tk_test_shotgun.find_one("PublishedFile", filters)

    # Getting version entity
    filters = [
        ["project", "is", tk_test_create_project],
        ["code", "is", "sven.png"],
    ]
    version_entity = tk_test_shotgun.find_one("Version", filters)

    # Make sure entities ids are identical.
    assert task_entity_fixture["id"] == task_entity["id"]
    assert publishedFile_entity_fixture["id"] == publishedFile_entity["id"]
    assert version_entity_fixture["id"] == version_entity["id"]
