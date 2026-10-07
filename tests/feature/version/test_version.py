from subprocess import CalledProcessError

import pytest
from pytest_mock import MockerFixture

from ddb.__main__ import load_registered_features, main
from ddb.config import config
from ddb.feature import features
from ddb.feature.core import CoreFeature
from ddb.feature.version import (
    VersionFeature,
    get_branch_from_vcs,
    get_hash_from_vcs,
    get_short_hash_from_vcs,
    get_tag_from_vcs,
    get_version_from_vcs,
    is_git_repository,
)


def _git_outputs(mocker: MockerFixture, *outputs: bytes | CalledProcessError):
    """
    Mock successive `git` calls, each output being either its stdout or the error it raises.
    """
    return mocker.patch("ddb.feature.version.run", side_effect=list(outputs))


_UNEXPECTED_ERROR = CalledProcessError(1, "git")
_NOT_A_REPOSITORY = CalledProcessError(128, "git")


class TestVcsAccessors:
    def test_is_git_repository(self, mocker: MockerFixture):
        _git_outputs(mocker, b".git")

        assert is_git_repository()

    def test_is_git_repository_outside_of_a_repository(self, mocker: MockerFixture):
        _git_outputs(mocker, _NOT_A_REPOSITORY)

        assert not is_git_repository()

    @pytest.mark.parametrize(
        "accessor",
        [get_tag_from_vcs, get_version_from_vcs, get_hash_from_vcs, get_short_hash_from_vcs, get_branch_from_vcs],
    )
    def test_accessor_returns_none_outside_of_a_repository(self, accessor, mocker: MockerFixture):
        _git_outputs(mocker, _NOT_A_REPOSITORY)

        assert accessor() is None

    @pytest.mark.parametrize(
        "accessor",
        [get_tag_from_vcs, get_version_from_vcs, get_hash_from_vcs, get_short_hash_from_vcs, get_branch_from_vcs],
    )
    def test_accessor_reraises_unexpected_errors(self, accessor, mocker: MockerFixture):
        _git_outputs(mocker, _UNEXPECTED_ERROR)

        with pytest.raises(CalledProcessError):
            accessor()


class TestDetachedHeadBranch:
    def test_local_branch_is_preferred(self, mocker: MockerFixture):
        _git_outputs(mocker, b"HEAD\n", b"some-branch\nanother-branch\n")

        assert get_branch_from_vcs() == "some-branch"

    def test_remote_branch_is_used_when_there_is_no_local_one(self, mocker: MockerFixture):
        _git_outputs(mocker, b"HEAD\n", b"", b"origin/some-branch\n")

        assert get_branch_from_vcs() == "some-branch"

    def test_head_is_kept_when_there_is_no_branch_at_all(self, mocker: MockerFixture):
        _git_outputs(mocker, b"HEAD\n", b"", b"")

        assert get_branch_from_vcs() == "HEAD"

    def test_head_is_kept_when_a_remote_ref_is_not_prefixed_by_its_remote(self, mocker: MockerFixture):
        _git_outputs(mocker, b"HEAD\n", b"", b"upstream/some-branch\n")

        assert get_branch_from_vcs() == "HEAD"

    def test_head_is_kept_when_local_refs_cannot_be_listed(self, mocker: MockerFixture):
        _git_outputs(mocker, b"HEAD\n", _NOT_A_REPOSITORY)

        assert get_branch_from_vcs() == "HEAD"

    def test_head_is_kept_when_remote_refs_cannot_be_listed(self, mocker: MockerFixture):
        _git_outputs(mocker, b"HEAD\n", b"", _NOT_A_REPOSITORY)

        assert get_branch_from_vcs() == "HEAD"

    def test_unexpected_error_on_local_refs_is_reraised(self, mocker: MockerFixture):
        _git_outputs(mocker, b"HEAD\n", _UNEXPECTED_ERROR)

        with pytest.raises(CalledProcessError):
            get_branch_from_vcs()

    def test_unexpected_error_on_remote_refs_is_reraised(self, mocker: MockerFixture):
        _git_outputs(mocker, b"HEAD\n", b"", _UNEXPECTED_ERROR)

        with pytest.raises(CalledProcessError):
            get_branch_from_vcs()


class TestVersionFeature:
    def test_empty_project_without_core(self, project_loader, mocker: MockerFixture):
        mocker.patch("ddb.feature.version.is_git_repository", is_git_repository)

        project_loader("no_repo")

        features.register(VersionFeature())
        load_registered_features()

    def test_empty_project_with_core(self, project_loader, mocker: MockerFixture):
        mocker.patch("ddb.feature.version.is_git_repository", is_git_repository)

        project_loader("no_repo")

        features.register(CoreFeature())
        features.register(VersionFeature())
        load_registered_features()

    def test_no_tag_repo(self, project_loader, mocker: MockerFixture):
        mocker.patch("ddb.feature.version.is_git_repository", is_git_repository)

        project_loader("no_tag_repo")

        main(["configure"], reset_disabled=True)

        assert config.data.get("version.hash") is not None
        assert config.data.get("version.short_hash") is not None
        assert config.data.get("version.branch") == "master"
        assert config.data.get("version.version") is None
        assert config.data.get("version.tag") is None

    def test_tag_repo(self, project_loader, mocker: MockerFixture):
        mocker.patch("ddb.feature.version.is_git_repository", is_git_repository)

        project_loader("tag_repo")

        main(["configure"], reset_disabled=True)

        assert config.data.get("version.hash") is not None
        assert config.data.get("version.short_hash") is not None
        assert config.data.get("version.branch") == "master"
        assert config.data.get("version.version") == "v1.0.0"
        assert config.data.get("version.tag") == "v1.0.0"

    def test_branch_repo(self, project_loader, mocker: MockerFixture):
        mocker.patch("ddb.feature.version.is_git_repository", is_git_repository)

        project_loader("branch_repo")

        main(["configure"], reset_disabled=True)

        assert config.data.get("version.hash") is not None
        assert config.data.get("version.short_hash") is not None
        assert config.data.get("version.branch") == "some-branch"
        assert config.data.get("version.version") is None
        assert config.data.get("version.tag") is None

    def test_detached_repo(self, project_loader, mocker: MockerFixture):
        mocker.patch("ddb.feature.version.is_git_repository", is_git_repository)

        project_loader("detached_repo")

        main(["configure"], reset_disabled=True)

        assert config.data.get("version.hash") is not None
        assert config.data.get("version.short_hash") is not None
        assert config.data.get("version.branch") == "develop"
        assert config.data.get("version.version") is None
        assert config.data.get("version.tag") is None

    def test_no_repo(self, project_loader, mocker: MockerFixture):
        mocker.patch("ddb.feature.version.is_git_repository", is_git_repository)

        project_loader("no_repo")

        main(["configure"], reset_disabled=True)

        assert config.data.get("version.hash") is None
        assert config.data.get("version.short_hash") is None
        assert config.data.get("version.branch") is None
        assert config.data.get("version.version") is None
        assert config.data.get("version.tag") is None

    def test_repo_no_commit(self, project_loader, mocker: MockerFixture):
        mocker.patch("ddb.feature.version.is_git_repository", is_git_repository)

        project_loader("repo_no_commit")

        main(["configure"], reset_disabled=True)

        assert config.data.get("version.hash") is None
        assert config.data.get("version.short_hash") is None
        assert config.data.get("version.branch") is None
        assert config.data.get("version.version") is None
        assert config.data.get("version.tag") is None
