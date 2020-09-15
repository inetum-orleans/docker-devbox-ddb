from pytest_mock import MockerFixture

from ddb.__main__ import main, load_registered_features
from ddb.config import config
from ddb.feature import features
from ddb.feature.core import CoreFeature
from ddb.feature.version import VersionFeature, is_git_repository


class TestVersionFeature:
    def test_empty_project_without_core(self, project_loader, mocker: MockerFixture):
        mocker.patch('ddb.feature.version.is_git_repository', is_git_repository)

        project_loader("no_repo")

        features.register(VersionFeature())
        load_registered_features()

    def test_empty_project_with_core(self, project_loader, mocker: MockerFixture):
        mocker.patch('ddb.feature.version.is_git_repository', is_git_repository)

        project_loader("no_repo")

        features.register(CoreFeature())
        features.register(VersionFeature())
        load_registered_features()

    def test_no_tag_repo(self, project_loader, mocker: MockerFixture):
        mocker.patch('ddb.feature.version.is_git_repository', is_git_repository)

        project_loader("no_tag_repo")

        main(["configure"], reset_disabled=True)

        assert config.data.get('version.hash') is not None
        assert config.data.get('version.short_hash') is not None
        assert config.data.get('version.branch') == 'master'
        assert config.data.get('version.version') is None
        assert config.data.get('version.tag') is None

    def test_tag_repo(self, project_loader, mocker: MockerFixture):
        mocker.patch('ddb.feature.version.is_git_repository', is_git_repository)

        project_loader("tag_repo")

        main(["configure"], reset_disabled=True)

        assert config.data.get('version.hash') is not None
        assert config.data.get('version.short_hash') is not None
        assert config.data.get('version.branch') == 'master'
        assert config.data.get('version.version') == 'v1.0.0'
        assert config.data.get('version.tag') == 'v1.0.0'

    def test_branch_repo(self, project_loader, mocker: MockerFixture):
        mocker.patch('ddb.feature.version.is_git_repository', is_git_repository)

        project_loader("branch_repo")

        main(["configure"], reset_disabled=True)

        assert config.data.get('version.hash') is not None
        assert config.data.get('version.short_hash') is not None
        assert config.data.get('version.branch') == 'some-branch'
        assert config.data.get('version.version') is None
        assert config.data.get('version.tag') is None

    def test_detached_repo(self, project_loader, mocker: MockerFixture):
        mocker.patch('ddb.feature.version.is_git_repository', is_git_repository)

        project_loader("detached_repo")

        main(["configure"], reset_disabled=True)

        assert config.data.get('version.hash') is not None
        assert config.data.get('version.short_hash') is not None
        assert config.data.get('version.branch') == 'develop'
        assert config.data.get('version.version') is None
        assert config.data.get('version.tag') is None

    def test_no_repo(self, project_loader, mocker: MockerFixture):
        mocker.patch('ddb.feature.version.is_git_repository', is_git_repository)

        project_loader("no_repo")

        main(["configure"], reset_disabled=True)

        assert config.data.get('version.hash') is None
        assert config.data.get('version.short_hash') is None
        assert config.data.get('version.branch') is None
        assert config.data.get('version.version') is None
        assert config.data.get('version.tag') is None

    def test_repo_no_commit(self, project_loader, mocker: MockerFixture):
        mocker.patch('ddb.feature.version.is_git_repository', is_git_repository)

        project_loader("repo_no_commit")

        main(["configure"], reset_disabled=True)

        assert config.data.get('version.hash') is None
        assert config.data.get('version.short_hash') is None
        assert config.data.get('version.branch') is None
        assert config.data.get('version.version') is None
        assert config.data.get('version.tag') is None
