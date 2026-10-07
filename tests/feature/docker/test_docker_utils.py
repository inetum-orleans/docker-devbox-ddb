from subprocess import CalledProcessError

import pytest
from pytest_mock import MockerFixture

from ddb.config import config
from ddb.feature.docker.lib.compose.config.errors import ConfigurationError
from ddb.feature.docker.utils import DockerComposeControl, DockerComposeYamlMissingException


@pytest.fixture
def _docker_commands():
    config.data["docker.docker_command"] = "docker"
    config.data["docker.docker_compose_command"] = "docker compose"


@pytest.fixture
def _compose_project(tmp_path, monkeypatch, _docker_commands):
    (tmp_path / "docker-compose.yml").write_text("services:\n  web:\n    image: nginx\n")
    monkeypatch.chdir(tmp_path)


@pytest.mark.usefixtures("_docker_commands")
class TestDockerComposeControlWithoutComposeFile:
    @pytest.fixture(autouse=True)
    def _empty_directory(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

    @pytest.mark.parametrize("call", [lambda c: c.up(), lambda c: c.stop("web"), lambda c: c.start("web")])
    def test_service_commands_require_a_compose_file(self, call):
        with pytest.raises(DockerComposeYamlMissingException):
            call(DockerComposeControl())

    @pytest.mark.parametrize("call", [lambda c: c.down(), lambda c: c.is_up("web"), lambda c: c.config()])
    def test_project_commands_require_a_compose_file(self, call):
        with pytest.raises(DockerComposeYamlMissingException):
            call(DockerComposeControl())

    def test_the_message_points_at_the_current_directory(self, tmp_path):
        with pytest.raises(DockerComposeYamlMissingException) as raised:
            DockerComposeControl().down()

        assert str(tmp_path) in raised.value.message


class TestDockerComposeControlConfiguration:
    def test_missing_docker_configuration_is_rejected(self):
        with pytest.raises(ConfigurationError):
            DockerComposeControl()

    @pytest.mark.usefixtures("_docker_commands")
    def test_commands_are_split(self):
        control = DockerComposeControl()

        assert control.docker_command == ["docker"]
        assert control.docker_compose_command == ["docker", "compose"]


@pytest.mark.usefixtures("_compose_project")
class TestDockerComposeControlCommands:
    @pytest.fixture
    def run(self, mocker: MockerFixture):
        return mocker.patch("ddb.feature.docker.utils.run", return_value=b"")

    def test_up_every_service(self, run):
        DockerComposeControl().up()

        run.assert_called_once_with("docker", "compose", "up", "-d")

    def test_up_a_single_service(self, run):
        DockerComposeControl().up("web")

        run.assert_called_once_with("docker", "compose", "up", "-d", "web")

    def test_stop_every_service(self, run):
        DockerComposeControl().stop(None)

        run.assert_called_once_with("docker", "compose", "stop")

    def test_stop_a_single_service(self, run):
        DockerComposeControl().stop("web")

        run.assert_called_once_with("docker", "compose", "stop", "web")

    def test_start_every_service(self, run):
        DockerComposeControl().start(None)

        run.assert_called_once_with("docker", "compose", "start")

    def test_start_a_single_service(self, run):
        DockerComposeControl().start("web")

        run.assert_called_once_with("docker", "compose", "start", "web")

    def test_down(self, run):
        DockerComposeControl().down()

        run.assert_called_once_with("docker", "compose", "down")

    def test_config_is_parsed(self, mocker: MockerFixture):
        mocker.patch("ddb.feature.docker.utils.run", return_value=b"services:\n  web:\n    image: nginx\n")

        assert DockerComposeControl().config() == {"services": {"web": {"image": "nginx"}}}

    def test_config_is_returned_raw_on_demand(self, mocker: MockerFixture):
        mocker.patch("ddb.feature.docker.utils.run", return_value=b"services: {}")

        assert DockerComposeControl().config(parse=False) == b"services: {}"


@pytest.mark.usefixtures("_compose_project")
class TestDockerComposeControlIsUp:
    def test_running_service(self, mocker: MockerFixture):
        mocker.patch("ddb.feature.docker.utils.run", side_effect=[b"deadbeef\n", b"cafe\ndeadbeef\n"])

        assert DockerComposeControl().is_up("web")

    def test_stopped_service(self, mocker: MockerFixture):
        mocker.patch("ddb.feature.docker.utils.run", side_effect=[b"deadbeef\n", b"cafe\n"])

        assert not DockerComposeControl().is_up("web")

    def test_service_without_container(self, mocker: MockerFixture):
        mocker.patch("ddb.feature.docker.utils.run", return_value=b"\n")

        assert not DockerComposeControl().is_up("web")

    def test_unknown_service(self, mocker: MockerFixture):
        error = CalledProcessError(1, "docker compose", stderr=b"no such service: web")
        mocker.patch("ddb.feature.docker.utils.run", side_effect=error)

        assert not DockerComposeControl().is_up("web")

    def test_unexpected_error_is_reraised(self, mocker: MockerFixture):
        error = CalledProcessError(1, "docker compose", stderr=b"cannot connect to the docker daemon")
        mocker.patch("ddb.feature.docker.utils.run", side_effect=error)

        with pytest.raises(CalledProcessError):
            DockerComposeControl().is_up("web")
