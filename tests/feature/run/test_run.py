import os

import pytest
from _pytest.capture import CaptureFixture

from ddb.__main__ import load_registered_features, register_actions_in_event_bus
from ddb.binary import binaries
from ddb.binary.binary import DefaultBinary
from ddb.config import config
from ddb.feature import features
from ddb.feature.core import CoreFeature
from ddb.feature.docker.binaries import DockerBinary
from ddb.feature.run import RunFeature, RunAction
from ddb.feature.shell import ShellFeature
from ddb.utils.docker import DockerUtils

docker_compose_bin = "docker-compose" if os.name != "nt" else "docker-compose.exe"


class TestRunFeature:
    def test_empty_project_without_core(self, project_loader):
        project_loader("empty")

        features.register(RunFeature())
        features.register(ShellFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = RunAction()
        action.execute()

    def test_empty_project_with_core(self, project_loader):
        project_loader("empty")

        features.register(CoreFeature())
        features.register(RunFeature())
        features.register(ShellFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = RunAction()
        action.execute()

    def test_run_missing_binary(self, project_loader):
        project_loader("empty")

        features.register(CoreFeature())
        features.register(RunFeature())
        features.register(ShellFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = RunAction()

        with pytest.raises(ValueError):
            action.run("missing")

    def test_run_existing_binary(self, project_loader, capsys: CaptureFixture):
        project_loader("empty")

        features.register(CoreFeature())
        features.register(RunFeature())
        features.register(ShellFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        binaries.register(DefaultBinary("test", ["some", "command"]))

        action = RunAction()
        action.run("test")

        read = capsys.readouterr()

        assert read.out == "some command\n"

    def test_run_docker_binary(self, project_loader, capsys: CaptureFixture):
        project_loader("empty")
        config.cwd = config.paths.project_home

        features.register(CoreFeature())
        features.register(RunFeature())
        features.register(ShellFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        binaries.register(DockerBinary("bin", "service", "/app"))

        action = RunAction()
        action.run("bin")

        read = capsys.readouterr()

        assert read.out == docker_compose_bin + " run --rm --workdir=/app/. service\n"

    def test_run_docker_binary_workdir(self, project_loader, capsys: CaptureFixture):
        project_loader("empty")
        config.cwd = os.path.join(config.paths.project_home, "sub")

        features.register(CoreFeature())
        features.register(RunFeature())
        features.register(ShellFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        binaries.register(DockerBinary("bin", "service", "/app"))

        action = RunAction()
        action.run("bin")

        read = capsys.readouterr()

        assert read.out == docker_compose_bin + " run --rm --workdir=/app/sub service\n"

    def test_run_docker_binary_workdir_outside(self, project_loader, capsys: CaptureFixture):
        project_loader("outside")
        config.cwd = os.path.join(config.paths.project_home, "../outside")

        features.register(CoreFeature())
        features.register(RunFeature())
        features.register(ShellFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        binaries.register(DockerBinary("bin", "service", "/app"))

        action = RunAction()
        action.run("bin")

        read = capsys.readouterr()

        cwd = config.cwd if config.cwd else os.getcwd()
        real_cwd = os.path.realpath(cwd)

        assert read.out == docker_compose_bin + " -f ../project/docker-compose.yml " \
                                                "run --rm "\
                                                f"--volume={real_cwd}:/app " \
                                                "--workdir=/app " \
                                                "service\n"

    def test_run_docker_binary_exe(self, project_loader, capsys: CaptureFixture):
        project_loader("exe")

        features.register(CoreFeature())
        features.register(RunFeature())
        features.register(ShellFeature())
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

        assert read.out == docker_compose_bin + " exec web echo\n"

        assert DockerUtils.is_container_up('web')

    def test_run_binary_condition(self, project_loader, capsys: CaptureFixture):
        project_loader("empty")

        features.register(CoreFeature())
        features.register(RunFeature())
        features.register(ShellFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        binary1 = DockerBinary("npm", "node1")
        binary2 = DockerBinary("npm", "node2")
        default_binary = DefaultBinary("npm", ["npm"])
        binary4 = DockerBinary("npm", "node4")
        binary_invalid_condition = DockerBinary("npm", "node5", condition="'another-value' in args")
        binary_valid_condition = DockerBinary("npm", "node6", condition="'some-value' in args")

        for bin in (binary1, binary2, default_binary, binary4, binary_invalid_condition, binary_valid_condition):
            binaries.register(bin)

        action = RunAction()
        action.run("npm", "some-value")

        read = capsys.readouterr()
        assert "node6" in read.out
