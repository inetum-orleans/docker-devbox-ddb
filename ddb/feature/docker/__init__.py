import os
import re
import socket
from collections.abc import Iterable

import psutil
from dotty_dict import Dotty

from ...action import Action
from ...config import config
from ...utils.compat import path_as_posix_fast
from ..feature import Feature, FeatureConfigurationAutoConfigureError
from ..schema import FeatureSchema
from .actions import (
    DockerComposeBinaryAction,
    DockerDisplayInfoAction,
    EmitDockerComposeConfigAction,
    LocalVolumesAction,
)
from .schema import DockerSchema


class DockerFeature(Feature):
    """
    Docker and docker-compose support.
    """

    @property
    def name(self) -> str:
        return "docker"

    @property
    def dependencies(self) -> Iterable[str]:
        return ["core"]

    @property
    def schema(self) -> type[FeatureSchema]:
        return DockerSchema

    @property
    def actions(self) -> Iterable[Action]:
        return (
            EmitDockerComposeConfigAction(),
            DockerComposeBinaryAction(),
            LocalVolumesAction(),
            DockerDisplayInfoAction(),
        )

    def _configure_defaults(self, feature_config: Dotty) -> None:
        self._configure_defaults_ip(feature_config)
        self._configure_defaults_user_from_name_and_group(feature_config)
        self._configure_defaults_user(feature_config)
        self._configure_defaults_path_mapping(feature_config)

    def _configure_defaults_ip(self, feature_config: Dotty) -> None:
        ip_address = feature_config.get("ip")
        if not ip_address:
            docker_host = os.environ.get("DOCKER_HOST")
            if docker_host:
                ip_match = re.match(r"(?:.*?)://(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*", docker_host)
                if ip_match:
                    ip_address = ip_match.group(1)

        try:
            if not ip_address:
                interface = feature_config.get("interface")
                docker_if = psutil.net_if_addrs().get(interface)
                if docker_if is None:
                    raise FeatureConfigurationAutoConfigureError(self, "ip", "Invalid network interface: " + interface)
                ip_address = next((addr.address for addr in docker_if if addr.family == socket.AF_INET), None)
                if not ip_address:
                    raise FeatureConfigurationAutoConfigureError(
                        self, "ip", "Can't get ip address from network interface configuration: " + interface
                    )
        except FeatureConfigurationAutoConfigureError:
            ip_address = "127.0.0.1"

        feature_config["ip"] = ip_address

    @staticmethod
    def _configure_defaults_user_from_name_and_group(feature_config: Dotty) -> None:
        uid = feature_config.get("user.uid")
        gid = feature_config.get("user.gid")

        if uid is None or gid is None:
            name = feature_config.get("user.name")
            if name:
                try:
                    import pwd

                    struct_passwd = pwd.getpwnam(name)
                    if uid is None:
                        uid = struct_passwd.pw_uid
                        feature_config["user.uid"] = uid
                    if gid is None:
                        gid = struct_passwd.pw_gid
                        feature_config["user.gid"] = gid
                except ImportError:
                    pass
                except KeyError:
                    pass

            group = feature_config.get("user.group")
            if group:
                try:
                    import grp

                    struct_group = grp.getgrnam(group)
                    gid = struct_group.gr_gid
                    feature_config["user.gid"] = gid
                except ImportError:
                    pass
                except KeyError:
                    pass

    @staticmethod
    def _configure_defaults_user(feature_config: Dotty) -> None:
        uid = feature_config.get("user.uid")
        if uid is None:
            try:
                uid = os.getuid()
            except AttributeError:
                uid = 1000
            feature_config["user.uid"] = uid

        gid = feature_config.get("user.gid")
        if gid is None:
            try:
                gid = os.getgid()
            except AttributeError:
                gid = 1000
            feature_config["user.gid"] = gid

    @staticmethod
    def _configure_defaults_path_mapping(feature_config: Dotty) -> None:
        """
        On windows, this generates a default path mapping matching docker-compose behavior when
        COMPOSE_CONVERT_WINDOWS_PATHS=1 is enabled.

        Drive letter should be lowercased to have the same behavior

        https://github.com/docker/compose/blob/f1059d75edf76e8856469108997c15bb46a41777/compose/config/types.py#L123-L132
        """
        path_mapping = feature_config.get("path_mapping")
        if path_mapping is None:
            path_mapping = {}
        if config.data.get("core.os") == "nt":
            for key in ("core.path.project_home", "core.path.ddb_home", "core.path.user_home", "core.path.home"):
                raw = config.data.get(key)
                if raw:
                    path_mapping[raw] = path_as_posix_fast(raw)
        sorted_path_mapping = {}
        for k in sorted(path_mapping, key=len, reverse=True):
            sorted_path_mapping[k] = path_mapping[k]
        feature_config["path_mapping"] = sorted_path_mapping
