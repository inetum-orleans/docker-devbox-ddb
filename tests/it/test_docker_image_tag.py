import os
import zipfile

import yaml
from dotty_dict import Dotty
from pytest_mock import MockerFixture

from ddb.__main__ import main
from ddb.config import Config
from ddb.feature.version import is_git_repository


class TestDockerImageTag:
    def test_image_tag_from_git_tag_jsonnet(self, project_loader, mocker: MockerFixture):
        Config.defaults = None

        mocker.patch('ddb.feature.version.is_git_repository', is_git_repository)

        project_loader("image_tag_from_git_tag")

        if os.path.exists("repo.zip"):
            with zipfile.ZipFile("repo.zip", 'r') as zip_ref:
                zip_ref.extractall(".")

        main(["configure"])

        assert os.path.exists("docker-compose.yml")

        with open("docker-compose.yml") as f:
            docker_compose = yaml.load(f, yaml.SafeLoader)
            assert Dotty(docker_compose).get('services.node.image') == 'some-registry/node:some-tag'

    def test_image_tag_from_git_branch_jsonnet(self, project_loader, mocker: MockerFixture):
        Config.defaults = None

        mocker.patch('ddb.feature.version.is_git_repository', is_git_repository)

        project_loader("image_tag_from_git_branch")

        if os.path.exists("repo.zip"):
            with zipfile.ZipFile("repo.zip", 'r') as zip_ref:
                zip_ref.extractall(".")

        main(["configure"])

        with open("docker-compose.yml") as f:
            docker_compose = yaml.load(f, yaml.SafeLoader)
            assert Dotty(docker_compose).get('services.node.image') == 'some-registry/node:some-branch'

    def test_image_tag_from_git_disabled_jsonnet(self, project_loader, mocker: MockerFixture):
        Config.defaults = None

        mocker.patch('ddb.feature.version.is_git_repository', is_git_repository)

        project_loader("image_tag_from_git_disabled")

        if os.path.exists("repo.zip"):
            with zipfile.ZipFile("repo.zip", 'r') as zip_ref:
                zip_ref.extractall(".")

        main(["configure"])

        with open("docker-compose.yml") as f:
            docker_compose = yaml.load(f, yaml.SafeLoader)
            assert Dotty(docker_compose).get('services.node.image') == 'some-registry/node'
