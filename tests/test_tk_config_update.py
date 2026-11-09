# Copyright (c) 2020 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import io
import json
import os
import subprocess
import urllib.error

import pytest
from ruamel import yaml

from tk_toolchain.cmd_line_tools import tk_config_update


# We'll create a copy of the config for this test so we can
# run the tool on it without modifying it.
@pytest.fixture(scope="module")
def cloned_config(tk_config_root, tmpdir_factory):
    """
    Clone tk-config-basic so we don't modify the user's repo.

    If this clone fails, it's likely because tag v1.6.1 is not in your
    copy of the repository or because tk-config-basic is missing.
    """
    tmp_path = str(tmpdir_factory.mktemp("config"))
    # We're cloning version v1.6.1 to ensure the test doesn't fail due to a change
    # in the config.
    subprocess.check_call(
        ["git", "clone", "--depth", "1", "--branch", "v1.6.1", tk_config_root, tmp_path]
    )
    return tmp_path


@pytest.fixture
def test_config(cloned_config):
    """
    Provides a fresh and clean copy of the test config. Any modifications
    made to the configuration will be reverted after after the test.
    """
    try:
        yield cloned_config
    finally:
        subprocess.call(["git", "reset", "--hard"], cwd=cloned_config)


def test_enumerate_files(cloned_config):
    """
    Ensure the tool enumerates files correctly.
    """
    files_found = [
        # strip the root of the path and flip the separators so we can
        # compare with the constant at the bottom of the file.
        path.replace(cloned_config + os.path.sep, "").replace(os.path.sep, "/")
        for path in tk_config_update.enumerate_yaml_files(cloned_config)
    ]
    assert set(files_found) == expected_config_files


@pytest.mark.parametrize(
    "descriptor, expected_result",
    [
        ({"something": "something"}, False),
        ({"type": "shotgun", "name": "something", "version": "231"}, False),
        ({"type": "app_store", "name": "something", "version": "231"}, True),
    ],
)
def test_is_app_store_descriptor(descriptor, expected_result):
    """
    Ensure appstore descriptor detection works.
    """
    assert tk_config_update.is_app_store_descriptor(descriptor) is expected_result


@pytest.mark.parametrize(
    "modified_file,path_to_descriptor,bundle,expected_version",
    [
        (os.path.join("core", "core_api.yml"), ["location"], "tk-core", "v0.18.0"),
        (
            "env/includes/common/frameworks.yml",
            ["frameworks", "tk-framework-shotgunutils_v5.x.x", "location"],
            "tk-framework-shotgunutils",
            "v5.0.0",
        ),
        (
            "env/includes/common/frameworks.yml",
            ["frameworks", "tk-framework-shotgunutils_v4.x.x", "location"],
            "tk-framework-shotgunutils",
            "v4.0.0",
        ),
        (
            "env/includes/common/apps.yml",
            ["common.apps.tk-multi-publish2.location"],
            "tk-multi-publish2",
            "v10.0.0",
        ),
        (
            "env/includes/common/engines.yml",
            ["common.engines.tk-3dsmax.location"],
            "tk-3dsmax",
            "v11.0.0",
        ),
    ],
)
def test_update_config(
    cloned_config,
    test_config,
    modified_file,
    path_to_descriptor,
    bundle,
    expected_version,
):
    """
    Ensure the update updates the right file and puts the right content in it.
    """
    # Make the path valid of the current os.
    modified_file = modified_file.replace("/", os.path.sep)
    updated_files = list(
        tk_config_update.update_files(test_config, bundle, expected_version)
    )
    assert updated_files == [os.path.join(test_config, modified_file)]

    with open(os.path.join(cloned_config, modified_file), "rt") as fh:
        _yaml = yaml.YAML()
        expected_cfg = _yaml.load(fh)

    with open(os.path.join(test_config, modified_file), "rt") as fh:
        _yaml = yaml.YAML()
        test_config = _yaml.load(fh)

    value = expected_cfg
    for key in path_to_descriptor:
        value = value[key]

    value["version"] = expected_version

    assert expected_cfg == test_config


@pytest.mark.parametrize(
    "url, expected",
    [
        (
            "https://github.com/shotgunsoftware/tk-config-basic.git",
            ("shotgunsoftware", "tk-config-basic"),
        ),
        (
            "https://github.com/shotgunsoftware/tk-config-basic",
            ("shotgunsoftware", "tk-config-basic"),
        ),
        (
            "git@github.com:shotgunsoftware/tk-config-default2.git",
            ("shotgunsoftware", "tk-config-default2"),
        ),
        (
            "ssh://git@github.com/shotgunsoftware/tk-config-rv.git",
            ("shotgunsoftware", "tk-config-rv"),
        ),
        (
            "https://x-access-token@github.com/shotgunsoftware/tk-config-rv.git",
            ("shotgunsoftware", "tk-config-rv"),
        ),
    ],
)
def test_parse_github_url(url, expected):
    """
    Ensure the owner and repository are extracted from GitHub URLs.
    """
    assert tk_config_update.parse_github_url(url) == expected


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/owner/repo.git",
        # Lookalike hosts.
        "https://notgithub.com/owner/repo.git",
        "https://github.com.evil.com/owner/repo.git",
        "git@notgithub.com:owner/repo.git",
        # github.com only appearing in the path or as a prefix.
        "https://example.com/github.com/owner/repo.git",
        "file:///tmp/github.com/owner/repo.git",
        "/tmp/github.com/owner/repo.git",
    ],
)
def test_parse_github_url_invalid(url):
    """
    Ensure non GitHub URLs are rejected.
    """
    with pytest.raises(ValueError):
        tk_config_update.parse_github_url(url)


def test_create_pull_request(monkeypatch):
    """
    Ensure the pull request is requested with the right payload and credentials.
    """
    sent = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self, *args):
            return json.dumps({"html_url": "https://github.com/o/r/pull/1"}).encode()

    def fake_urlopen(request):
        sent["request"] = request
        return FakeResponse()

    monkeypatch.setattr(tk_config_update.urllib.request, "urlopen", fake_urlopen)

    url = tk_config_update.create_pull_request(
        "o", "r", "secret", "title", head="my-branch", base="master", body="body"
    )

    request = sent["request"]
    assert url == "https://github.com/o/r/pull/1"
    assert request.full_url == "https://api.github.com/repos/o/r/pulls"
    assert request.get_method() == "POST"
    assert request.get_header("Authorization") == "Bearer secret"
    assert json.loads(request.data) == {
        "base": "master",
        "body": "body",
        "head": "my-branch",
        "title": "title",
    }


def test_create_pull_request_error_does_not_leak_token(monkeypatch):
    """
    Ensure a GitHub refusal is reported without the token.
    """

    def fake_urlopen(request):
        raise urllib.error.HTTPError(
            request.full_url, 422, "Unprocessable", {}, io.BytesIO(b"already exists")
        )

    monkeypatch.setattr(tk_config_update.urllib.request, "urlopen", fake_urlopen)

    with pytest.raises(RuntimeError) as exc_info:
        tk_config_update.create_pull_request(
            "o", "r", "secret", "title", head="b", base="master", body=""
        )
    assert "already exists" in str(exc_info.value)
    assert "secret" not in str(exc_info.value)


def test_main_requires_token_to_push(monkeypatch):
    """
    Ensure we fail before cloning anything if we can't open a pull request.
    """
    monkeypatch.delenv(tk_config_update.GITHUB_TOKEN_ENV_VAR, raising=False)
    with pytest.raises(RuntimeError):
        tk_config_update.main(
            [
                "https://github.com/shotgunsoftware/tk-config-basic.git",
                "tk-core",
                "v1.0.0",
                "--push-changes",
            ]
        )


def test_repository_branch_operations(tmp_path):
    """
    Ensure the branch helpers behave against a real (local) remote.
    """
    remote = str(tmp_path / "remote.git")
    subprocess.check_call(["git", "init", "--bare", "-b", "main", remote])

    seed = str(tmp_path / "seed")
    subprocess.check_call(["git", "init", "-b", "main", seed])
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@example.com"]
    subprocess.check_call(git + ["commit", "--allow-empty", "-m", "init"], cwd=seed)
    subprocess.check_call(["git", "push", remote, "main"], cwd=seed)

    repo = tk_config_update.Repository.clone("file://" + remote)
    assert repo.current_branch == "main"
    assert not repo.remote_branch_exists("update/tk-core-v1.0.0")

    repo.checkout_new_branch("update/tk-core-v1.0.0")
    assert repo.current_branch == "update/tk-core-v1.0.0"

    subprocess.check_call(
        git + ["commit", "--allow-empty", "-m", "change"], cwd=repo.root
    )
    repo.push("update/tk-core-v1.0.0")
    assert repo.remote_branch_exists("update/tk-core-v1.0.0")


CONFIG_URL = "https://github.com/shotgunsoftware/tk-config-basic.git"

_GIT_IDENTITY = ["git", "-c", "user.name=t", "-c", "user.email=t@example.com"]


@pytest.fixture
def fake_github(monkeypatch, tmp_path):
    """
    Make CONFIG_URL point to a local bare repository, so main() can clone and push
    for real without ever reaching GitHub, and stub out the pull request creation.

    :returns: Tuple of (path to the bare remote, list of pull request calls).
    """
    remote = tmp_path / "remote.git"
    subprocess.check_call(["git", "init", "--bare", "-b", "main", str(remote)])

    seed = tmp_path / "seed"
    subprocess.check_call(["git", "init", "-b", "main", str(seed)])
    (seed / "apps.yml").write_text(
        "location:\n"
        "  type: app_store\n"
        "  name: tk-core\n"
        "  version: v1.0.0\n"
    )
    subprocess.check_call(["git", "add", "apps.yml"], cwd=str(seed))
    subprocess.check_call(_GIT_IDENTITY + ["commit", "-m", "init"], cwd=str(seed))
    subprocess.check_call(["git", "push", str(remote), "main"], cwd=str(seed))

    # Redirect the GitHub URL to the local remote.
    for name, value in (
        ("GIT_CONFIG_COUNT", "1"),
        ("GIT_CONFIG_KEY_0", "url.{0}.insteadOf".format(remote.as_uri())),
        ("GIT_CONFIG_VALUE_0", CONFIG_URL),
        ("GIT_AUTHOR_NAME", "t"),
        ("GIT_AUTHOR_EMAIL", "t@example.com"),
        ("GIT_COMMITTER_NAME", "t"),
        ("GIT_COMMITTER_EMAIL", "t@example.com"),
        (tk_config_update.GITHUB_TOKEN_ENV_VAR, "secret"),
    ):
        monkeypatch.setenv(name, value)

    pull_requests = []

    def fake_create_pull_request(owner, repo, token, title, head, base, body):
        pull_requests.append(
            {
                "base": base,
                "body": body,
                "head": head,
                "owner": owner,
                "repo": repo,
                "title": title,
                "token": token,
            }
        )
        return "https://github.com/{0}/{1}/pull/1".format(owner, repo)

    monkeypatch.setattr(
        tk_config_update, "create_pull_request", fake_create_pull_request
    )

    return str(remote), pull_requests


def _remote_branches(remote):
    """
    List the branches of a repository.
    """
    output = subprocess.check_output(
        ["git", "branch", "--format=%(refname:short)"], cwd=remote, text=True
    )
    return set(output.split())


def test_main_opens_pull_request(fake_github):
    """
    Ensure the update is pushed to a branch and a pull request is opened, leaving
    the default branch untouched.
    """
    remote, pull_requests = fake_github
    main_before = subprocess.check_output(
        ["git", "rev-parse", "main"], cwd=remote, text=True
    )

    assert (
        tk_config_update.main([CONFIG_URL, "tk-core", "v2.0.0", "--push-changes"]) == 0
    )

    assert _remote_branches(remote) == {"main", "update/tk-core-v2.0.0"}
    assert (
        subprocess.check_output(["git", "rev-parse", "main"], cwd=remote, text=True)
        == main_before
    )
    updated = subprocess.check_output(
        ["git", "show", "update/tk-core-v2.0.0:apps.yml"], cwd=remote, text=True
    )
    assert "version: v2.0.0" in updated

    assert pull_requests == [
        {
            "base": "main",
            "body": (
                "Release notes: "
                "https://github.com/shotgunsoftware/tk-core/releases/tag/v2.0.0"
            ),
            "head": "update/tk-core-v2.0.0",
            "owner": "shotgunsoftware",
            "repo": "tk-config-basic",
            "title": "Updated tk-core to v2.0.0",
            "token": "secret",
        }
    ]


def test_main_without_push_changes(fake_github):
    """
    Ensure nothing is pushed and no pull request is opened without --push-changes.
    """
    remote, pull_requests = fake_github

    assert tk_config_update.main([CONFIG_URL, "tk-core", "v2.0.0"]) == 0

    assert _remote_branches(remote) == {"main"}
    assert pull_requests == []


def test_main_nothing_to_update(fake_github):
    """
    Ensure no branch is pushed and no pull request is opened if no file changed.
    """
    remote, pull_requests = fake_github

    arguments = [CONFIG_URL, "tk-toolkit-app", "v2.0.0", "--push-changes"]
    assert tk_config_update.main(arguments) == 0

    assert _remote_branches(remote) == {"main"}
    assert pull_requests == []


def test_main_existing_branch(fake_github):
    """
    Ensure we refuse to touch a branch that already exists, rather than force it.
    """
    remote, pull_requests = fake_github
    subprocess.check_call(
        ["git", "branch", "update/tk-core-v2.0.0", "main"], cwd=remote
    )
    branch_before = subprocess.check_output(
        ["git", "rev-parse", "update/tk-core-v2.0.0"], cwd=remote, text=True
    )

    with pytest.raises(RuntimeError, match="already exists"):
        tk_config_update.main([CONFIG_URL, "tk-core", "v2.0.0", "--push-changes"])

    assert pull_requests == []
    assert (
        subprocess.check_output(
            ["git", "rev-parse", "update/tk-core-v2.0.0"], cwd=remote, text=True
        )
        == branch_before
    )


# This will of files will not change over time as the repository for the tests
# was cloned from a tag.
expected_config_files = set(
    [
        "env/includes/desktop2/site.yml",
        "env/includes/3dsmax/shot_step.yml",
        "env/includes/aftereffects/shot.yml",
        "env/includes/houdini/shot_step.yml",
        "azure-pipelines.yml",
        "env/includes/maya/project.yml",
        "env/includes/photoshopcc/shot.yml",
        "env/includes/maya/shot_step.yml",
        "env/includes/vred/apps.yml",
        "env/includes/3dsmax/site.yml",
        "env/includes/vred/project.yml",
        "core/core_api.yml",
        "env/includes/shell/project.yml",
        "env/includes/photoshopcc/asset_step.yml",
        "env/includes/flame/shot.yml",
        "env/asset_step.yml",
        "env/project.yml",
        "env/includes/alias/site.yml",
        "env/includes/maya/site.yml",
        "env/includes/maya/apps.yml",
        "env/site.yml",
        "env/includes/aftereffects/project.yml",
        "env/includes/photoshopcc/project.yml",
        "env/includes/aftereffects/apps.yml",
        "env/includes/photoshopcc/shot_step.yml",
        "env/includes/houdini/project.yml",
        "env/includes/flame/project.yml",
        "env/includes/common/apps.yml",
        "env/includes/houdini/asset_step.yml",
        "env/includes/houdini/shot.yml",
        "env/includes/shell/apps.yml",
        "env/includes/shotgun/all.yml",
        "env/includes/houdini/site.yml",
        "env/includes/desktop2/all.yml",
        "env/includes/alias/project.yml",
        "env/includes/maya/shot.yml",
        "env/publishedfile.yml",
        "env/includes/common/engines.yml",
        "env/shot.yml",
        "env/includes/desktop/site.yml",
        "env/includes/maya/asset_step.yml",
        "env/includes/3dsmax/project.yml",
        "env/includes/nuke/project.yml",
        "env/includes/3dsmax/asset_step.yml",
        "env/includes/flame/asset_step.yml",
        "env/includes/nuke/site.yml",
        "env/includes/nuke/asset_step.yml",
        "env/includes/nuke/apps.yml",
        "env/includes/3dsmax/shot.yml",
        "env/includes/common/settings/tk-multi-publish2.yml",
        "env/includes/alias/apps.yml",
        "env/includes/vred/site.yml",
        "env/includes/shell/shot.yml",
        "env/includes/common/frameworks.yml",
        "env/includes/photoshopcc/apps.yml",
        "env/includes/nuke/shot.yml",
        "env/shot_step.yml",
        "env/includes/shell/site.yml",
        "env/includes/aftereffects/asset_step.yml",
        "info.yml",
        "env/includes/houdini/apps.yml",
        "env/includes/shell/asset_step.yml",
        "env/includes/shell/shot_step.yml",
        "env/includes/aftereffects/shot_step.yml",
        "env/includes/flame/shot_step.yml",
        "env/includes/3dsmax/apps.yml",
        "core/roots.yml",
        "env/includes/desktop/project.yml",
        "env/includes/photoshopcc/site.yml",
        "env/includes/nuke/shot_step.yml",
        "env/includes/aftereffects/site.yml",
        # Added after v1.3.0
        "env/includes/shotgun/version.yml",
        "env/version.yml",
        "env/includes/alias/asset_step.yml",
        "env/includes/vred/asset_step.yml",
        "env/playlist.yml",
        "env/includes/shotgun/playlist.yml",
    ]
)
