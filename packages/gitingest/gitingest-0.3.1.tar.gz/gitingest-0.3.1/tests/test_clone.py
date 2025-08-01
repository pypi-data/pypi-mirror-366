"""Tests for the ``clone`` module.

These tests cover various scenarios for cloning repositories, verifying that the appropriate Git commands are invoked
and handling edge cases such as nonexistent URLs, timeouts, redirects, and specific commits or branches.
"""

from __future__ import annotations

import asyncio
import sys
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

import httpx
import pytest
from starlette.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

from gitingest.clone import clone_repo
from gitingest.schemas import CloneConfig
from gitingest.utils.exceptions import AsyncTimeoutError
from gitingest.utils.git_utils import check_repo_exists
from tests.conftest import DEMO_COMMIT, DEMO_URL, LOCAL_REPO_PATH

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockerFixture


# All cloning-related tests assume (unless explicitly overridden) that the repository exists.
# Apply the check-repo patch automatically so individual tests don't need to repeat it.
pytestmark = pytest.mark.usefixtures("repo_exists_true")

GIT_INSTALLED_CALLS = 2 if sys.platform == "win32" else 1


@pytest.mark.asyncio
async def test_clone_with_commit(repo_exists_true: AsyncMock, run_command_mock: AsyncMock) -> None:
    """Test cloning a repository with a specific commit hash.

    Given a valid URL and a commit hash:
    When ``clone_repo`` is called,
    Then the repository should be cloned and checked out at that commit.
    """
    expected_call_count = GIT_INSTALLED_CALLS + 3  # ensure_git_installed + clone + fetch + checkout
    commit_hash = "a" * 40  # Simulating a valid commit hash
    clone_config = CloneConfig(
        url=DEMO_URL,
        local_path=LOCAL_REPO_PATH,
        commit=commit_hash,
        branch="main",
    )

    await clone_repo(clone_config)

    repo_exists_true.assert_any_call(clone_config.url, token=None)
    assert_standard_calls(run_command_mock, clone_config, commit=commit_hash)
    assert run_command_mock.call_count == expected_call_count


@pytest.mark.asyncio
async def test_clone_without_commit(repo_exists_true: AsyncMock, run_command_mock: AsyncMock) -> None:
    """Test cloning a repository when no commit hash is provided.

    Given a valid URL and no commit hash:
    When ``clone_repo`` is called,
    Then only the clone_repo operation should be performed (no checkout).
    """
    expected_call_count = GIT_INSTALLED_CALLS + 4  # ensure_git_installed + resolve_commit + clone + fetch + checkout
    clone_config = CloneConfig(url=DEMO_URL, local_path=LOCAL_REPO_PATH, commit=None, branch="main")

    await clone_repo(clone_config)

    repo_exists_true.assert_any_call(clone_config.url, token=None)
    assert_standard_calls(run_command_mock, clone_config, commit=DEMO_COMMIT)
    assert run_command_mock.call_count == expected_call_count


@pytest.mark.asyncio
async def test_clone_nonexistent_repository(repo_exists_true: AsyncMock) -> None:
    """Test cloning a nonexistent repository URL.

    Given an invalid or nonexistent URL:
    When ``clone_repo`` is called,
    Then a ValueError should be raised with an appropriate error message.
    """
    clone_config = CloneConfig(
        url="https://github.com/user/nonexistent-repo",
        local_path=LOCAL_REPO_PATH,
        commit=None,
        branch="main",
    )
    # Override the default fixture behaviour for this test
    repo_exists_true.return_value = False

    with pytest.raises(ValueError, match="Repository not found"):
        await clone_repo(clone_config)

    repo_exists_true.assert_any_call(clone_config.url, token=None)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("status_code", "expected"),
    [
        (HTTP_200_OK, True),
        (HTTP_401_UNAUTHORIZED, False),
        (HTTP_403_FORBIDDEN, False),
        (HTTP_404_NOT_FOUND, False),
    ],
)
async def test_check_repo_exists(status_code: int, *, expected: bool, mocker: MockerFixture) -> None:
    """Verify that ``check_repo_exists`` interprets httpx results correctly."""
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client  # context-manager protocol
    mock_client.head.return_value = httpx.Response(status_code=status_code)
    mocker.patch("httpx.AsyncClient", return_value=mock_client)

    result = await check_repo_exists(DEMO_URL)

    assert result is expected


@pytest.mark.asyncio
async def test_clone_with_custom_branch(run_command_mock: AsyncMock) -> None:
    """Test cloning a repository with a specified custom branch.

    Given a valid URL and a branch:
    When ``clone_repo`` is called,
    Then the repository should be cloned shallowly to that branch.
    """
    expected_call_count = GIT_INSTALLED_CALLS + 4  # ensure_git_installed + resolve_commit + clone + fetch + checkout
    clone_config = CloneConfig(url=DEMO_URL, local_path=LOCAL_REPO_PATH, branch="feature-branch")

    await clone_repo(clone_config)

    assert_standard_calls(run_command_mock, clone_config, commit=DEMO_COMMIT)
    assert run_command_mock.call_count == expected_call_count


@pytest.mark.asyncio
async def test_git_command_failure(run_command_mock: AsyncMock) -> None:
    """Test cloning when the Git command fails during execution.

    Given a valid URL, but ``run_command`` raises a RuntimeError:
    When ``clone_repo`` is called,
    Then a RuntimeError should be raised with the correct message.
    """
    clone_config = CloneConfig(url=DEMO_URL, local_path=LOCAL_REPO_PATH)

    run_command_mock.side_effect = RuntimeError("Git is not installed or not accessible. Please install Git first.")

    with pytest.raises(RuntimeError, match="Git is not installed or not accessible"):
        await clone_repo(clone_config)


@pytest.mark.asyncio
async def test_clone_default_shallow_clone(run_command_mock: AsyncMock) -> None:
    """Test cloning a repository with the default shallow clone options.

    Given a valid URL and no branch or commit:
    When ``clone_repo`` is called,
    Then the repository should be cloned with ``--depth=1`` and ``--single-branch``.
    """
    expected_call_count = GIT_INSTALLED_CALLS + 4  # ensure_git_installed + resolve_commit + clone + fetch + checkout
    clone_config = CloneConfig(url=DEMO_URL, local_path=LOCAL_REPO_PATH)

    await clone_repo(clone_config)

    assert_standard_calls(run_command_mock, clone_config, commit=DEMO_COMMIT)
    assert run_command_mock.call_count == expected_call_count


@pytest.mark.asyncio
async def test_clone_commit(run_command_mock: AsyncMock) -> None:
    """Test cloning when a commit hash is provided.

    Given a valid URL and a commit hash:
    When ``clone_repo`` is called,
    Then the repository should be cloned and checked out at that commit.
    """
    expected_call_count = GIT_INSTALLED_CALLS + 3  # ensure_git_installed + clone + fetch + checkout
    commit_hash = "a" * 40  # Simulating a valid commit hash
    clone_config = CloneConfig(url=DEMO_URL, local_path=LOCAL_REPO_PATH, commit=commit_hash)

    await clone_repo(clone_config)

    assert_standard_calls(run_command_mock, clone_config, commit=commit_hash)
    assert run_command_mock.call_count == expected_call_count


@pytest.mark.asyncio
async def test_check_repo_exists_with_redirect(mocker: MockerFixture) -> None:
    """Test ``check_repo_exists`` when a redirect (302) is returned.

    Given a URL that responds with "302 Found":
    When ``check_repo_exists`` is called,
    Then it should return ``False``, indicating the repo is inaccessible.
    """
    mock_exec = mocker.patch("asyncio.create_subprocess_exec", new_callable=AsyncMock)
    mock_process = AsyncMock()
    mock_process.communicate.return_value = (b"302\n", b"")
    mock_process.returncode = 0  # Simulate successful request
    mock_exec.return_value = mock_process

    repo_exists = await check_repo_exists(DEMO_URL)

    assert repo_exists is False


@pytest.mark.asyncio
async def test_clone_with_timeout(run_command_mock: AsyncMock) -> None:
    """Test cloning a repository when a timeout occurs.

    Given a valid URL, but ``run_command`` times out:
    When ``clone_repo`` is called,
    Then an ``AsyncTimeoutError`` should be raised to indicate the operation exceeded time limits.
    """
    clone_config = CloneConfig(url=DEMO_URL, local_path=LOCAL_REPO_PATH)

    run_command_mock.side_effect = asyncio.TimeoutError

    with pytest.raises(AsyncTimeoutError, match="Operation timed out after"):
        await clone_repo(clone_config)


@pytest.mark.asyncio
async def test_clone_branch_with_slashes(tmp_path: Path, run_command_mock: AsyncMock) -> None:
    """Test cloning a branch with slashes in the name.

    Given a valid repository URL and a branch name with slashes:
    When ``clone_repo`` is called,
    Then the repository should be cloned and checked out at that branch.
    """
    branch_name = "fix/in-operator"
    local_path = tmp_path / "gitingest"
    expected_call_count = GIT_INSTALLED_CALLS + 4  # ensure_git_installed + resolve_commit + clone + fetch + checkout
    clone_config = CloneConfig(url=DEMO_URL, local_path=str(local_path), branch=branch_name)

    await clone_repo(clone_config)

    assert_standard_calls(run_command_mock, clone_config, commit=DEMO_COMMIT)
    assert run_command_mock.call_count == expected_call_count


@pytest.mark.asyncio
async def test_clone_creates_parent_directory(tmp_path: Path, run_command_mock: AsyncMock) -> None:
    """Test that ``clone_repo`` creates parent directories if they don't exist.

    Given a local path with non-existent parent directories:
    When ``clone_repo`` is called,
    Then it should create the parent directories before attempting to clone.
    """
    expected_call_count = GIT_INSTALLED_CALLS + 4  # ensure_git_installed + resolve_commit + clone + fetch + checkout
    nested_path = tmp_path / "deep" / "nested" / "path" / "repo"

    clone_config = CloneConfig(url=DEMO_URL, local_path=str(nested_path))

    await clone_repo(clone_config)

    assert nested_path.parent.exists()
    assert_standard_calls(run_command_mock, clone_config, commit=DEMO_COMMIT)
    assert run_command_mock.call_count == expected_call_count


@pytest.mark.asyncio
async def test_clone_with_specific_subpath(run_command_mock: AsyncMock) -> None:
    """Test cloning a repository with a specific subpath.

    Given a valid repository URL and a specific subpath:
    When ``clone_repo`` is called,
    Then the repository should be cloned with sparse checkout enabled and the specified subpath.
    """
    # ensure_git_installed + resolve_commit + clone + sparse-checkout + fetch + checkout
    subpath = "src/docs"
    expected_call_count = GIT_INSTALLED_CALLS + 5
    clone_config = CloneConfig(url=DEMO_URL, local_path=LOCAL_REPO_PATH, subpath=subpath)

    await clone_repo(clone_config)

    # Verify the clone command includes sparse checkout flags
    assert_partial_clone_calls(run_command_mock, clone_config, commit=DEMO_COMMIT)
    assert run_command_mock.call_count == expected_call_count


@pytest.mark.asyncio
async def test_clone_with_commit_and_subpath(run_command_mock: AsyncMock) -> None:
    """Test cloning a repository with both a specific commit and subpath.

    Given a valid repository URL, commit hash, and subpath:
    When ``clone_repo`` is called,
    Then the repository should be cloned with sparse checkout enabled,
    checked out at the specific commit, and only include the specified subpath.
    """
    subpath = "src/docs"
    expected_call_count = GIT_INSTALLED_CALLS + 4  # ensure_git_installed + clone + sparse-checkout + fetch + checkout
    commit_hash = "a" * 40  # Simulating a valid commit hash
    clone_config = CloneConfig(url=DEMO_URL, local_path=LOCAL_REPO_PATH, commit=commit_hash, subpath=subpath)

    await clone_repo(clone_config)

    assert_partial_clone_calls(run_command_mock, clone_config, commit=commit_hash)
    assert run_command_mock.call_count == expected_call_count


@pytest.mark.asyncio
async def test_clone_with_include_submodules(run_command_mock: AsyncMock) -> None:
    """Test cloning a repository with submodules included.

    Given a valid URL and ``include_submodules=True``:
    When ``clone_repo`` is called,
    Then the repository should be cloned with ``--recurse-submodules`` in the git command.
    """
    # ensure_git_installed + resolve_commit + clone + fetch + checkout + checkout submodules
    expected_call_count = GIT_INSTALLED_CALLS + 5
    clone_config = CloneConfig(url=DEMO_URL, local_path=LOCAL_REPO_PATH, branch="main", include_submodules=True)

    await clone_repo(clone_config)

    assert_standard_calls(run_command_mock, clone_config, commit=DEMO_COMMIT)
    assert_submodule_calls(run_command_mock, clone_config)
    assert run_command_mock.call_count == expected_call_count


def assert_standard_calls(mock: AsyncMock, cfg: CloneConfig, commit: str, *, partial_clone: bool = False) -> None:
    """Assert that the standard clone sequence of git commands was called."""
    mock.assert_any_call("git", "--version")
    if sys.platform == "win32":
        mock.assert_any_call("git", "config", "core.longpaths")

    # Clone
    clone_cmd = ["git", "clone", "--single-branch", "--no-checkout", "--depth=1"]
    if partial_clone:
        clone_cmd += ["--filter=blob:none", "--sparse"]
    mock.assert_any_call(*clone_cmd, cfg.url, cfg.local_path)

    mock.assert_any_call("git", "-C", cfg.local_path, "fetch", "--depth=1", "origin", commit)
    mock.assert_any_call("git", "-C", cfg.local_path, "checkout", commit)


def assert_partial_clone_calls(mock: AsyncMock, cfg: CloneConfig, commit: str) -> None:
    """Assert that the partial clone sequence of git commands was called."""
    assert_standard_calls(mock, cfg, commit=commit, partial_clone=True)
    mock.assert_any_call("git", "-C", cfg.local_path, "sparse-checkout", "set", cfg.subpath)


def assert_submodule_calls(mock: AsyncMock, cfg: CloneConfig) -> None:
    """Assert that submodule update commands were called."""
    mock.assert_any_call("git", "-C", cfg.local_path, "submodule", "update", "--init", "--recursive", "--depth=1")
