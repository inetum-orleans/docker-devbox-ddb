from pathlib import Path

import docker
import pytest
import yaml

from ddb.__main__ import load_registered_features, register_actions_in_event_bus, register_default_caches
from ddb.event import events
from ddb.feature import features
from ddb.feature.core import CoreFeature
from ddb.feature.fixuid import FixuidDockerComposeAction, FixuidFeature


class TestFixuidFeature:
    def test_empty_project_without_core(self, project_loader):
        project_loader("empty")

        features.register(FixuidFeature())
        load_registered_features()

        action = FixuidDockerComposeAction()
        action.execute(docker_compose_config={})

    def test_empty_project_with_core(self, project_loader):
        project_loader("empty")

        features.register(CoreFeature())
        features.register(FixuidFeature())
        load_registered_features()

        action = FixuidDockerComposeAction()
        action.execute(docker_compose_config={})

    @pytest.mark.parametrize(
        "project",
        [
            "from-scratch-empty",
            "from-scratch-with-entrypoint",
            "from-scratch-with-entrypoint-multiple-line",
            "from-scratch-with-entrypoint-string",
            "from-scratch-with-entrypoint-string-no-quotes",
            "from-php-missing-configuration",
            "from-php-empty",
            "from-php-with-entrypoint-only",
            "from-php-with-entrypoint-and-cmd",
            "from-php-user",
            "from-php-root-user",
        ],
    )
    def test_fixuid(self, project_loader, project):
        project_loader(project)
        register_default_caches()

        features.register(FixuidFeature())
        load_registered_features()

        with Path("docker-compose.yml").open() as config_file:
            config = yaml.load(config_file, yaml.SafeLoader)

        action = FixuidDockerComposeAction()
        action.execute(docker_compose_config=config)

        with (Path("docker") / "Dockerfile.expected").open() as f:
            expected = f.read()
        with (Path("docker") / "Dockerfile").open() as f:
            content = f.read()
        assert content == expected

        if project in ["from-php-missing-configuration"]:
            assert not (Path("docker") / "fixuid.tar.gz").exists()
        else:
            assert (Path("docker") / "fixuid.tar.gz").exists()

        if "scratch" not in project:
            client = docker.from_env()
            image = client.images.build(path="docker")
            assert image

    def test_from_mysql_fixuid_removed(self, project_loader):
        project_loader("from-mysql-fixuid-removed")
        register_default_caches()

        features.register(FixuidFeature())
        load_registered_features()
        register_actions_in_event_bus(fail_fast=True)

        with Path("docker-compose.yml").open() as config_file:
            config = yaml.load(config_file, yaml.SafeLoader)

        events.docker.docker_compose_config(config)

        with (Path("docker") / "Dockerfile.expected").open() as f:
            expected = f.read()
        with (Path("docker") / "Dockerfile").open() as f:
            content = f.read()
        assert content == expected

        assert (Path("docker") / "fixuid.tar.gz").exists()

        (Path("docker") / "fixuid.yml").unlink()
        events.file.deleted(str(Path("docker") / "fixuid.yml"))

        with (Path("docker") / "Dockerfile.removed.expected").open() as f:
            expected = f.read()
        with (Path("docker") / "Dockerfile").open() as f:
            content = f.read()
        assert content == expected

        assert not (Path("docker") / "fixuid.tar.gz").exists()

    def test_no_fixuid(self, project_loader):
        project_loader("no-fixuid")
        register_default_caches()

        features.register(FixuidFeature())
        load_registered_features()
        register_actions_in_event_bus(fail_fast=True)

        with Path("docker-compose.yml").open() as config_file:
            config = yaml.load(config_file, yaml.SafeLoader)

        events.docker.docker_compose_config(config)

        with (Path("docker") / "Dockerfile.expected").open() as f:
            expected = f.read()
        with (Path("docker") / "Dockerfile").open() as f:
            content = f.read()
        assert content == expected

        assert not (Path("docker") / "fixuid.tar.gz").exists()

    def test_fixuid_manual(self, project_loader):
        project_loader("fixuid-manual")
        register_default_caches()

        features.register(FixuidFeature())
        load_registered_features()
        register_actions_in_event_bus(fail_fast=True)

        with Path("docker-compose.yml").open() as config_file:
            config = yaml.load(config_file, yaml.SafeLoader)

        events.docker.docker_compose_config(config)

        with (Path("docker") / "Dockerfile.expected").open() as f:
            expected = f.read()
        with (Path("docker") / "Dockerfile").open() as f:
            content = f.read()
        assert content == expected

        assert (Path("docker") / "fixuid.tar.gz").exists()

    def test_fixuid_manual_install(self, project_loader):
        project_loader("fixuid-manual-install")
        register_default_caches()

        features.register(FixuidFeature())
        load_registered_features()
        register_actions_in_event_bus(fail_fast=True)

        with Path("docker-compose.yml").open() as config_file:
            config = yaml.load(config_file, yaml.SafeLoader)

        events.docker.docker_compose_config(config)

        with (Path("docker") / "Dockerfile.expected").open() as f:
            expected = f.read()
        with (Path("docker") / "Dockerfile").open() as f:
            content = f.read()
        assert content == expected

        assert (Path("docker") / "fixuid.tar.gz").exists()

    def test_fixuid_manual_entrypoint(self, project_loader):
        project_loader("fixuid-manual-entrypoint")
        register_default_caches()

        features.register(FixuidFeature())
        load_registered_features()
        register_actions_in_event_bus(fail_fast=True)

        with Path("docker-compose.yml").open() as config_file:
            config = yaml.load(config_file, yaml.SafeLoader)

        events.docker.docker_compose_config(config)

        with (Path("docker") / "Dockerfile.expected").open() as f:
            expected = f.read()
        with (Path("docker") / "Dockerfile").open() as f:
            content = f.read()
        assert content == expected

        assert (Path("docker") / "fixuid.tar.gz").exists()
