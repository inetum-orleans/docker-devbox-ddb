import os

import docker
import pytest

from ddb.__main__ import load_registered_features, register_default_caches
from ddb.feature import features
from ddb.feature.core import CoreFeature
from ddb.feature.docker import DockerFeature, FixuidAction


class TestDockerFeature:
    def test_empty_project_without_core(self, project_loader):
        project_loader("empty")

        features.register(DockerFeature())
        load_registered_features()

        action = FixuidAction()
        action.execute()

    def test_empty_project_with_core(self, project_loader):
        project_loader("empty")

        features.register(CoreFeature())
        features.register(DockerFeature())
        load_registered_features()

        action = FixuidAction()
        action.execute()

    @pytest.mark.parametrize("project", [
        "fixuid-from-scratch-empty",
        "fixuid-from-scratch-with-entrypoint",
        "fixuid-from-scratch-with-entrypoint-multiple-line",
        "fixuid-from-scratch-with-entrypoint-string",
        "fixuid-from-scratch-with-entrypoint-string-no-quotes",
        "fixuid-from-php-missing-configuration",
        "fixuid-from-php-empty",
        "fixuid-from-php-with-entrypoint-only",
        "fixuid-from-php-with-entrypoint-and-cmd",
        "fixuid-from-php-user"
    ])
    def test_fixuid(self, project_loader, project):
        project_loader(project)
        register_default_caches()

        features.register(DockerFeature())
        load_registered_features()

        action = FixuidAction()
        action.execute()

        with open(os.path.join("docker", "Dockerfile.expected"), "r") as f:
            expected = f.read()
        with open(os.path.join("docker", "Dockerfile"), "r") as f:
            content = f.read()
        assert content == expected

        if project in ["fixuid-from-php-missing-configuration"]:
            assert not os.path.exists(os.path.join("docker", "fixuid.tar.gz"))
        else:
            assert os.path.exists(os.path.join("docker", "fixuid.tar.gz"))

        if "scratch" not in project:
            client = docker.from_env()
            image = client.images.build(path="docker")
            assert image
