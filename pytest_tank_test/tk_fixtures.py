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
import os
from tk_toolchain.authentication import get_toolkit_user
from tk_toolchain.testing import create_unique_name


@pytest.fixture(scope="session")
def tk_test_shotgun():
    """
    Getting credentials from TK_TOOLCHAIN
    """
    sg = get_toolkit_user().create_sg_connection()

    return sg


@pytest.fixture(scope="session")
def tk_test_current_user(tk_test_shotgun):
    """
    Get current user

    :returns: The current user id and name
    """
    user = get_toolkit_user()
    username = tk_test_shotgun.find_one(
        "HumanUser", [["login", "is", str(user)]], ["name"]
    )

    return username


@pytest.fixture(scope="session")
def tk_test_project(tk_test_shotgun):
    """
    Generates a fresh Shotgun Project to use with the UI Automation.

    :returns: Current project name and id
    """
    import sgtk

    # Create or update the integration_tests local storage with the current test run.
    # Cannot use a unique name for storage_name because Workfiles2 automation
    # is using an advanced custom config and it has storage name harcoded in roots.yml
    storage_name = "Toolkit UI Automation"
    local_storage = tk_test_shotgun.find_one(
        "LocalStorage", [["code", "is", storage_name]], ["code"]
    )
    if local_storage is None:
        local_storage = tk_test_shotgun.create("LocalStorage", {"code": storage_name})
    # Always update local storage path
    local_storage["path"] = os.path.expandvars("${SHOTGUN_CURRENT_REPO_ROOT}")
    if sgtk.util.is_windows():
        storage_key = "windows_path"
    elif sgtk.util.is_linux():
        storage_key = "linux_path"
    elif sgtk.util.is_macos():
        storage_key = "mac_path"
    else:
        raise Exception("Unknown platform")

    tk_test_shotgun.update(
        "LocalStorage", local_storage["id"], {storage_key: local_storage["path"]}
    )

    # Make sure there is not already an automation project created
    project_name = create_unique_name("Toolkit UI Automation")
    filters = [["name", "is", project_name]]
    existed_project = tk_test_shotgun.find_one("Project", filters)
    if existed_project is not None:
        tk_test_shotgun.delete(existed_project["type"], existed_project["id"])

    # Create a new project with the Film VFX Template
    project_data = {
        "sg_description": "Project Created by Automation",
        "name": project_name,
        "tank_name": project_name,
    }
    new_project = tk_test_shotgun.create("Project", project_data)

    return new_project


@pytest.fixture(scope="session")
def tk_test_entities(tk_test_project, tk_test_shotgun, tk_test_current_user):
    """
    Creates Shotgun entities which will be used in different test cases.

    :returns: model_task, publish_file and version informations
    """
    # Create a Sequence to be used by the Shot creation
    sequence_data = {
        "project": tk_test_project,
        "code": "seq_001",
        "sg_status_list": "ip",
    }
    new_sequence = tk_test_shotgun.create("Sequence", sequence_data)

    # Validate if Automation shot task template exists
    shot_template_filters = [["code", "is", "Automation Shot Task Template"]]
    existed_shot_template = tk_test_shotgun.find_one(
        "TaskTemplate", shot_template_filters
    )
    if existed_shot_template is not None:
        tk_test_shotgun.delete(
            existed_shot_template["type"], existed_shot_template["id"]
        )
    # Create a shot task templates
    shot_template_data = {
        "code": "Automation Shot Task Template",
        "description": "This shot task template was created by the Toolkit UI automation",
        "entity_type": "Shot",
    }
    shot_task_template = tk_test_shotgun.create("TaskTemplate", shot_template_data)

    # Create Comp and Light tasks
    for shot_task_name in ["Comp", "Light"]:
        # Get the Pipeline step task name
        shot_pipeline_step_filter = [["code", "is", shot_task_name]]
        shot_pipeline_step = tk_test_shotgun.find_one("Step", shot_pipeline_step_filter)
        # Create task
        shot_task_data = {
            "content": shot_task_name,
            "step": shot_pipeline_step,
            "task_template": shot_task_template,
        }
        tk_test_shotgun.create("Task", shot_task_data)

    # Validate if Automation asset task template exists
    asset_template_filters = [["code", "is", "Automation Asset Task Template"]]
    existed_asset_template = tk_test_shotgun.find_one(
        "TaskTemplate", asset_template_filters
    )
    if existed_asset_template is not None:
        tk_test_shotgun.delete(
            existed_asset_template["type"], existed_asset_template["id"]
        )
    # Create an asset task templates
    asset_template_data = {
        "code": "Automation Asset Task Template",
        "description": "This asset task template was created by the Toolkit UI automation",
        "entity_type": "Asset",
    }
    asset_task_template = tk_test_shotgun.create("TaskTemplate", asset_template_data)

    # Create Model and Rig tasks
    for task_name in ["Model", "Rig"]:
        # Get the Pipeline step task name
        pipeline_step_filter = [["code", "is", task_name]]
        pipeline_step = tk_test_shotgun.find_one("Step", pipeline_step_filter)
        # Create task
        task_data = {
            "content": task_name,
            "step": pipeline_step,
            "task_template": asset_task_template,
        }
        tk_test_shotgun.create("Task", task_data)

    # Create a new shot
    shot_data = {
        "project": tk_test_project,
        "sg_sequence": new_sequence,
        "code": "shot_001",
        "description": "This shot was created by the Toolkit UI automation",
        "sg_status_list": "ip",
        "task_template": shot_task_template,
    }
    tk_test_shotgun.create("Shot", shot_data)

    # Create a new asset
    asset_data = {
        "project": tk_test_project,
        "code": "AssetAutomation",
        "description": "This asset was created by the Toolkit UI automation",
        "sg_status_list": "ip",
        "sg_asset_type": "Character",
        "task_template": asset_task_template,
    }
    asset = tk_test_shotgun.create("Asset", asset_data)

    # File to publish
    file_to_publish = os.path.join(
        os.path.expandvars("${TK_TEST_FIXTURES}"), "files", "images", "sven.png"
    )

    # Create a version an upload to it
    version_data = {
        "project": tk_test_project,
        "code": "sven.png",
        "description": "This version was created by the Toolkit UI automation",
        "entity": asset,
    }
    version = tk_test_shotgun.create("Version", version_data)
    # Upload a version to the published file
    tk_test_shotgun.upload(
        "Version", version["id"], file_to_publish, "sg_uploaded_movie"
    )

    # Find the model task to publish to
    filters = [
        ["project", "is", tk_test_project],
        ["entity.Asset.code", "is", asset["code"]],
        ["step.Step.code", "is", "model"],
    ]
    fields = ["sg_status_list"]
    model_task = tk_test_shotgun.find_one("Task", filters, fields)

    # Create a published file
    publish_data = {
        "project": tk_test_project,
        "code": "sven.png",
        "name": "sven.png",
        "description": "This file was published by the Toolkit UI automation",
        "path": {"local_path": file_to_publish},
        "entity": asset,
        "task": model_task,
        "version_number": 1,
        "version": version,
        "image": file_to_publish,
    }
    publish_file = tk_test_shotgun.create("PublishedFile", publish_data)

    # Assign current user to the task model
    tk_test_shotgun.update(
        "Task",
        model_task["id"],
        {
            "content": "Model",
            "task_assignees": [{"type": "HumanUser", "id": tk_test_current_user["id"]}],
        },
    )

    return (model_task, publish_file, version)
