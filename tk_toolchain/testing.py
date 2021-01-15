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
import subprocess
import time
import os
import sys
from tk_toolchain.authentication import get_toolkit_user

try:
    from MA.UI import topwindows
except ImportError:
    pytestmark = pytest.mark.skip()

@pytest.fixture(scope="session")
def shotgun():
    """
    Getting credentials from TK_TOOLCHAIN
    """
    sg = get_toolkit_user().create_sg_connection()

    return sg


@pytest.fixture(scope="session")
def sg_project(shotgun):
    """
    Generates a fresh Shotgun Project to use with the UI Automation.
    """
    # Create or update the integration_tests local storage with the current test run
    storage_name = create_unique_name("Toolkit UI Automation")
    local_storage = shotgun.find_one(
        "LocalStorage", [["code", "is", storage_name]], ["code"]
    )
    if local_storage is None:
        local_storage = shotgun.create("LocalStorage", {"code": storage_name})
    # Always update local storage path
    local_storage["path"] = os.path.expandvars("${SHOTGUN_CURRENT_REPO_ROOT}")
    shotgun.update(
        "LocalStorage", local_storage["id"], {"windows_path": local_storage["path"]}
    )

    # Make sure there is not already an automation project created
    project_name = create_unique_name("Toolkit UI Automation")
    filters = [["name", "is", project_name]]
    existed_project = shotgun.find_one("Project", filters)
    if existed_project is not None:
        shotgun.delete(existed_project["type"], existed_project["id"])

    # Create a new project with the Film VFX Template
    project_data = {
        "sg_description": "Project Created by Automation",
        "name": project_name,
    }
    new_project = shotgun.create("Project", project_data)

    return new_project


@pytest.fixture(scope="session")
def sg_entities(sg_project, shotgun):
    """
    Creates Shotgun entities which will be used in different test cases.
    """
    # Create a Sequence to be used by the Shot creation
    sequence_data = {
        "project": sg_project,
        "code": "seq_001",
        "sg_status_list": "ip",
    }
    new_sequence = shotgun.create("Sequence", sequence_data)

    # Validate if Automation shot task template exists
    shot_template_filters = [["code", "is", "Automation Shot Task Template"]]
    existed_shot_template = shotgun.find_one("TaskTemplate", shot_template_filters)
    if existed_shot_template is not None:
        shotgun.delete(existed_shot_template["type"], existed_shot_template["id"])
    # Create a shot task templates
    shot_template_data = {
        "code": "Automation Shot Task Template",
        "description": "This shot task template was created by the Toolkit UI automation",
        "entity_type": "Shot",
    }
    shot_task_template = shotgun.create("TaskTemplate", shot_template_data)

    # Create Comp and Light tasks
    for shot_task_name in ["Comp", "Light"]:
        # Get the Pipeline step task name
        shot_pipeline_step_filter = [["code", "is", shot_task_name]]
        shot_pipeline_step = shotgun.find_one("Step", shot_pipeline_step_filter)
        # Create task
        shot_task_data = {
            "content": shot_task_name,
            "step": shot_pipeline_step,
            "task_template": shot_task_template,
        }
        shotgun.create("Task", shot_task_data)

    # Validate if Automation asset task template exists
    asset_template_filters = [["code", "is", "Automation Asset Task Template"]]
    existed_asset_template = shotgun.find_one("TaskTemplate", asset_template_filters)
    if existed_asset_template is not None:
        shotgun.delete(existed_asset_template["type"], existed_asset_template["id"])
    # Create an asset task templates
    asset_template_data = {
        "code": "Automation Asset Task Template",
        "description": "This asset task template was created by the Toolkit UI automation",
        "entity_type": "Asset",
    }
    asset_task_template = shotgun.create("TaskTemplate", asset_template_data)

    # Create Model and Rig tasks
    for task_name in ["Model", "Rig"]:
        # Get the Pipeline step task name
        pipeline_step_filter = [["code", "is", task_name]]
        pipeline_step = shotgun.find_one("Step", pipeline_step_filter)
        # Create task
        task_data = {
            "content": task_name,
            "step": pipeline_step,
            "task_template": asset_task_template,
        }
        shotgun.create("Task", task_data)

    # Create a new shot
    shot_data = {
        "project": sg_project,
        "sg_sequence": new_sequence,
        "code": "shot_001",
        "description": "This shot was created by the Toolkit UI automation",
        "sg_status_list": "ip",
        "task_template": shot_task_template,
    }
    shotgun.create("Shot", shot_data)

    # Create a new asset
    asset_data = {
        "project": sg_project,
        "code": "AssetAutomation",
        "description": "This asset was created by the Toolkit UI automation",
        "sg_status_list": "ip",
        "sg_asset_type": "Character",
        "task_template": asset_task_template,
    }
    asset = shotgun.create("Asset", asset_data)

    # Get the publish_file_type id to be passed in the publish creation
    published_file_type_filters = [["code", "is", "Image"]]
    published_file_type = shotgun.find_one(
        "PublishedFileType", published_file_type_filters
    )

    # File to publish
    file_to_publish = os.path.join(
        os.path.expandvars("${TK_TEST_FIXTURES}"), "files", "images", "sven.png"
    )

    # Create a version an upload to it
    version_data = {
        "project": sg_project,
        "code": "sven.png",
        "description": "This version was created by the Toolkit UI automation",
        "entity": asset,
    }
    version = shotgun.create("Version", version_data)
    # Upload a version to the published file
    shotgun.upload("Version", version["id"], file_to_publish, "sg_uploaded_movie")

    # Find the model task to publish to
    filters = [
        ["project", "is", sg_project],
        ["entity.Asset.code", "is", asset["code"]],
        ["step.Step.code", "is", "model"],
    ]
    fields = ["sg_status_list"]
    model_task = shotgun.find_one("Task", filters, fields)

    # Create a published file
    publish_data = {
        "project": sg_project,
        "code": "sven.png",
        "name": "sven.png",
        "description": "This file was published by the Toolkit UI automation",
        "published_file_type": published_file_type,
        "path": {"local_path": file_to_publish},
        "entity": asset,
        "task": model_task,
        "version_number": 1,
        "version": version,
        "image": file_to_publish,
    }
    publish_file = shotgun.create("PublishedFile", publish_data)

    # Assign a task to the current user
    # Find current user
    user = get_toolkit_user()
    current_user = shotgun.find_one("HumanUser", [["login", "is", str(user)]], ["name"])
    # Assign current user to the task model
    shotgun.update(
        "Task",
        model_task["id"],
        {
            "content": "Model",
            "task_assignees": [{"type": "HumanUser", "id": current_user["id"]}],
        },
    )

    return (model_task, publish_file, version, current_user)


def create_unique_name(name):
    """
    Create a unique name.

    When ``SHOTGUN_TEST_ENTITY_SUFFIX`` is set, the suffix is added to the name. This can be useful
    in a CI environment where multiple resources can be created on a server and each need a unique
    name.

    It is the responsibility of the CI environment to set ``SHOTGUN_TEST_ENTITY_SUFFIX`` for this method
    to work. If the environment variable is not set, the name is returned as is.

    :param str name: Name that needs to be made unique.

    :returns: The name with a suffix is one was specified by the environment variable.
    """
    if "SHOTGUN_TEST_ENTITY_SUFFIX" in os.environ:
        project_name = name + " - " + os.environ["SHOTGUN_TEST_ENTITY_SUFFIX"]
    else:
        project_name = name

    return project_name
