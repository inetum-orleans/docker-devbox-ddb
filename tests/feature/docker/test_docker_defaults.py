import os
import socket
import sys
from collections import namedtuple

import pytest
from dotty_dict import Dotty
from pytest_mock import MockerFixture

from ddb.config import config
from ddb.feature.docker import DockerFeature

_snicaddr = namedtuple("snicaddr", ["family", "address"])


class TestConfigureDefaultsIp:
    def test_configured_ip_is_kept(self):
        feature_config = Dotty({"ip": "10.0.0.1", "interface": "docker0"})

        DockerFeature()._configure_defaults_ip(feature_config)

        assert feature_config["ip"] == "10.0.0.1"

    def test_ip_is_read_from_docker_host(self, monkeypatch):
        monkeypatch.setenv("DOCKER_HOST", "tcp://192.168.99.100:2376")
        feature_config = Dotty({"interface": "docker0"})

        DockerFeature()._configure_defaults_ip(feature_config)

        assert feature_config["ip"] == "192.168.99.100"

    def test_ip_is_read_from_the_interface(self, monkeypatch, mocker: MockerFixture):
        monkeypatch.delenv("DOCKER_HOST", raising=False)
        mocker.patch(
            "psutil.net_if_addrs",
            return_value={"docker0": [_snicaddr(socket.AF_INET6, "::1"), _snicaddr(socket.AF_INET, "172.17.0.1")]},
        )
        feature_config = Dotty({"interface": "docker0"})

        DockerFeature()._configure_defaults_ip(feature_config)

        assert feature_config["ip"] == "172.17.0.1"

    def test_docker_host_without_ip_falls_back_to_the_interface(self, monkeypatch, mocker: MockerFixture):
        monkeypatch.setenv("DOCKER_HOST", "unix:///var/run/docker.sock")
        mocker.patch("psutil.net_if_addrs", return_value={"docker0": [_snicaddr(socket.AF_INET, "172.17.0.1")]})
        feature_config = Dotty({"interface": "docker0"})

        DockerFeature()._configure_defaults_ip(feature_config)

        assert feature_config["ip"] == "172.17.0.1"

    def test_unknown_interface_falls_back_to_localhost(self, monkeypatch, mocker: MockerFixture):
        monkeypatch.delenv("DOCKER_HOST", raising=False)
        mocker.patch("psutil.net_if_addrs", return_value={})
        feature_config = Dotty({"interface": "docker0"})

        DockerFeature()._configure_defaults_ip(feature_config)

        assert feature_config["ip"] == "127.0.0.1"

    def test_interface_without_ipv4_address_falls_back_to_localhost(self, monkeypatch, mocker: MockerFixture):
        monkeypatch.delenv("DOCKER_HOST", raising=False)
        mocker.patch("psutil.net_if_addrs", return_value={"docker0": [_snicaddr(socket.AF_INET6, "::1")]})
        feature_config = Dotty({"interface": "docker0"})

        DockerFeature()._configure_defaults_ip(feature_config)

        assert feature_config["ip"] == "127.0.0.1"


@pytest.mark.skipif("os.name == 'nt'")
class TestConfigureDefaultsUserFromNameAndGroup:
    def test_uid_and_gid_are_read_from_the_user_name(self, mocker: MockerFixture):
        mocker.patch("pwd.getpwnam", return_value=mocker.Mock(pw_uid=1042, pw_gid=1043))
        feature_config = Dotty({"user": {"name": "some-user"}})

        DockerFeature._configure_defaults_user_from_name_and_group(feature_config)

        assert feature_config["user.uid"] == 1042
        assert feature_config["user.gid"] == 1043

    def test_gid_is_read_from_the_group_name(self, mocker: MockerFixture):
        mocker.patch("grp.getgrnam", return_value=mocker.Mock(gr_gid=1044))
        feature_config = Dotty({"user": {"group": "some-group"}})

        DockerFeature._configure_defaults_user_from_name_and_group(feature_config)

        assert feature_config["user.gid"] == 1044

    def test_group_wins_over_user_name(self, mocker: MockerFixture):
        mocker.patch("pwd.getpwnam", return_value=mocker.Mock(pw_uid=1042, pw_gid=1043))
        mocker.patch("grp.getgrnam", return_value=mocker.Mock(gr_gid=1044))
        feature_config = Dotty({"user": {"name": "some-user", "group": "some-group"}})

        DockerFeature._configure_defaults_user_from_name_and_group(feature_config)

        assert feature_config["user.uid"] == 1042
        assert feature_config["user.gid"] == 1044

    def test_unknown_user_and_group_are_ignored(self, mocker: MockerFixture):
        mocker.patch("pwd.getpwnam", side_effect=KeyError)
        mocker.patch("grp.getgrnam", side_effect=KeyError)
        feature_config = Dotty({"user": {"name": "some-user", "group": "some-group"}})

        DockerFeature._configure_defaults_user_from_name_and_group(feature_config)

        assert feature_config.get("user.uid") is None
        assert feature_config.get("user.gid") is None

    def test_already_configured_uid_and_gid_are_kept(self, mocker: MockerFixture):
        getpwnam = mocker.patch("pwd.getpwnam")
        feature_config = Dotty({"user": {"name": "some-user", "uid": 1, "gid": 2}})

        DockerFeature._configure_defaults_user_from_name_and_group(feature_config)

        getpwnam.assert_not_called()


class TestConfigureDefaultsUserWithoutPwdAndGrp:
    """
    `pwd` and `grp` are missing on windows, where the user name and group cannot be resolved.
    """

    @pytest.fixture(autouse=True)
    def _no_pwd_and_grp(self, mocker: MockerFixture):
        mocker.patch.dict(sys.modules, {"pwd": None, "grp": None})

    def test_user_name_is_ignored(self):
        feature_config = Dotty({"user": {"name": "some-user"}})

        DockerFeature._configure_defaults_user_from_name_and_group(feature_config)

        assert feature_config.get("user.uid") is None

    def test_group_name_is_ignored(self):
        feature_config = Dotty({"user": {"group": "some-group"}})

        DockerFeature._configure_defaults_user_from_name_and_group(feature_config)

        assert feature_config.get("user.gid") is None


class TestConfigureDefaultsUser:
    def test_uid_and_gid_default_to_the_current_process_ones(self, mocker: MockerFixture):
        mocker.patch.object(os, "getuid", return_value=1042, create=True)
        mocker.patch.object(os, "getgid", return_value=1043, create=True)
        feature_config = Dotty({})

        DockerFeature._configure_defaults_user(feature_config)

        assert feature_config["user.uid"] == 1042
        assert feature_config["user.gid"] == 1043

    def test_uid_and_gid_default_to_1000_when_the_platform_has_none(self, mocker: MockerFixture):
        mocker.patch.object(os, "getuid", side_effect=AttributeError, create=True)
        mocker.patch.object(os, "getgid", side_effect=AttributeError, create=True)
        feature_config = Dotty({})

        DockerFeature._configure_defaults_user(feature_config)

        assert feature_config["user.uid"] == 1000
        assert feature_config["user.gid"] == 1000

    def test_configured_uid_and_gid_are_kept(self):
        feature_config = Dotty({"user": {"uid": 1, "gid": 2}})

        DockerFeature._configure_defaults_user(feature_config)

        assert feature_config["user.uid"] == 1
        assert feature_config["user.gid"] == 2


class TestConfigureDefaultsPathMapping:
    def test_path_mapping_defaults_to_an_empty_mapping(self):
        feature_config = Dotty({})

        DockerFeature._configure_defaults_path_mapping(feature_config)

        assert feature_config["path_mapping"] == {}

    def test_path_mapping_is_sorted_from_the_longest_source_path(self):
        feature_config = Dotty({"path_mapping": {"/short": "/a", "/a/longer/one": "/b"}})

        DockerFeature._configure_defaults_path_mapping(feature_config)

        assert list(feature_config["path_mapping"]) == ["/a/longer/one", "/short"]

    def test_configuration_paths_are_mapped_to_posix_on_windows(self):
        config.data["core.os"] = "nt"
        config.data["core.path.project_home"] = r"C:\project"
        config.data["core.path.home"] = r"C:\Users\some-user\.docker-devbox"
        feature_config = Dotty({})

        DockerFeature._configure_defaults_path_mapping(feature_config)

        assert feature_config["path_mapping"] == {
            r"C:\Users\some-user\.docker-devbox": "/c/Users/some-user/.docker-devbox",
            r"C:\project": "/c/project",
        }
