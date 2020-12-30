import os
from typing import Iterable

import pytest
from _pytest.capture import CaptureFixture

from ddb.__main__ import load_registered_features, register_actions_in_event_bus
from ddb.binary import binaries, Binary
from ddb.config import config
from ddb.feature import features
from ddb.feature.core import CoreFeature
from ddb.feature.docker.binaries import DockerBinary
from ddb.feature.run import RunFeature, RunAction
from ddb.utils.docker import DockerUtils


class BinaryMock(Binary):
    def pre_execute(self):
        return True

    def __init__(self, name, *command):
        self._name = name
        self._command = command

    def command(self, *args) -> Iterable[str]:
        return self._command

    @property
    def name(self) -> str:
        return self._name

    @property
    def in_folder(self) -> None:
        return None

    def is_same(self, binary) -> bool:
        return self.command() == binary.command()


class TestRunFeature:
    def test_empty_project_without_core(self, project_loader):
        project_loader("empty")

        features.register(RunFeature())
        load_registered_features()

        action = RunAction()
        action.execute()

    def test_empty_project_with_core(self, project_loader):
        project_loader("empty")

        features.register(CoreFeature())
        features.register(RunFeature())
        load_registered_features()

        action = RunAction()
        action.execute()

    def test_run_missing_binary(self, project_loader):
        project_loader("empty")

        features.register(CoreFeature())
        features.register(RunFeature())
        load_registered_features()

        action = RunAction()

        with pytest.raises(ValueError):
            action.run("missing")

    def test_run_existing_binary(self, project_loader, capsys: CaptureFixture):
        project_loader("empty")

        features.register(CoreFeature())
        features.register(RunFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        binaries.register(BinaryMock("test", "some", "command"))

        action = RunAction()
        action.run("test")

        read = capsys.readouterr()

        assert "some command" in read.out

    def test_run_docker_binary(self, project_loader, capsys: CaptureFixture):
        project_loader("empty")
        config.cwd = config.paths.project_home

        features.register(CoreFeature())
        features.register(RunFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        binaries.register(DockerBinary("bin", "service", "/app"))

        action = RunAction()
        action.run("bin")

        read = capsys.readouterr()

        assert "docker-compose run --rm --workdir=/app/. service" in read.out

    def test_run_docker_binary_workdir(self, project_loader, capsys: CaptureFixture):
        project_loader("empty")
        config.cwd = os.path.join(config.paths.project_home, "sub")

        features.register(CoreFeature())
        features.register(RunFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        binaries.register(DockerBinary("bin", "service", "/app"))

        action = RunAction()
        action.run("bin")

        read = capsys.readouterr()

        assert "docker-compose run --rm --workdir=/app/sub service" in read.out

    def test_run_docker_binary_exe(self, project_loader, capsys: CaptureFixture):
        project_loader("exe")

        features.register(CoreFeature())
        features.register(RunFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        binaries.register(DockerBinary("echo",
                                       docker_compose_service="web",
                                       args="echo",
                                       exe=True))

        DockerUtils.service_stop('web')
        assert not DockerUtils.is_container_up('web')

        action = RunAction()
        action.run("echo")

        read = capsys.readouterr()

        assert "docker-compose exec web echo" in read.out

        assert DockerUtils.is_container_up('web')

    def test_run_docker_binary_exe_in_folder(self, project_loader, capsys: CaptureFixture):
        project_loader("exe")

        features.register(CoreFeature())
        features.register(RunFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        binaries.register(DockerBinary("echo",
                                       docker_compose_service="web",
                                       args="echo",
                                       exe=True,
                                       in_folder='project'))

        config.cwd = config.data['core']['path']['project_home']

        action = RunAction()

        try:
            action.run("echo")
        except ValueError as e:
            assert e.args[0] == ' binary named name "echo" is not available in your current working directory'

        config.cwd = os.path.join(config.cwd, 'project')

        action.run("echo")

        read = capsys.readouterr()

        assert 'docker-compose exec web echo' in read.out
