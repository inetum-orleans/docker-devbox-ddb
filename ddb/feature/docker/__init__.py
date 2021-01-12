# -*- coding: utf-8 -*-
import os
import re
from typing import Iterable, ClassVar

import netifaces
from dotty_dict import Dotty

from .actions import EmitDockerComposeConfigAction, DockerComposeBinaryAction, LocalVolumesAction, \
    DockerDisplayInfoAction
from .schema import DockerSchema
from ..feature import Feature, FeatureConfigurationAutoConfigureError
from ..schema import FeatureSchema
from ...action import Action


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
    def schema(self) -> ClassVar[FeatureSchema]:
        return DockerSchema

    @property
    def actions(self) -> Iterable[Action]:
        return (
            EmitDockerComposeConfigAction(),
            DockerComposeBinaryAction(),
            LocalVolumesAction(),
            DockerDisplayInfoAction()
        )

    def _configure_defaults(self, feature_config: Dotty):
        self._configure_defaults_ip(feature_config)
        self._configure_defaults_user_from_name_and_group(feature_config)
        self._configure_defaults_user(feature_config)

    def _configure_defaults_ip(self, feature_config):
        ip_address = feature_config.get('ip')
        if not ip_address:
            docker_host = os.environ.get('DOCKER_HOST')
            if docker_host:
                ip_match = re.match(r"(?:.*?)://(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*", docker_host)
                if ip_match:
                    ip_address = ip_match.group(1)

        try:
            if not ip_address:
                interface = feature_config.get('interface')
                try:
                    docker_if = netifaces.ifaddresses(interface)
                except ValueError as err:
                    raise FeatureConfigurationAutoConfigureError(self, 'ip',
                                                                 "Invalid network interface: " + interface) from err
                if docker_if and netifaces.AF_INET in docker_if:
                    docker_af_inet = docker_if[netifaces.AF_INET][0]
                    ip_address = docker_af_inet['addr']
                else:
                    raise FeatureConfigurationAutoConfigureError(self, 'ip',
                                                                 "Can't get ip address "
                                                                 "from network interface configuration: " + interface)
        except FeatureConfigurationAutoConfigureError as error:
            if os.path.exists('/var/run/docker.sock'):
                ip_address = '127.0.0.1'
            else:
                raise error

        feature_config['ip'] = ip_address

    @staticmethod
    def _configure_defaults_user_from_name_and_group(feature_config):
        uid = feature_config.get('user.uid')
        gid = feature_config.get('user.gid')

        if uid is None or gid is None:
            name = feature_config.get('user.name')
            if name:
                try:
                    import pwd  # pylint:disable=import-outside-toplevel
                    struct_passwd = pwd.getpwnam(name)
                    if uid is None:
                        uid = struct_passwd.pw_uid
                        feature_config['user.uid'] = uid
                    if gid is None:
                        gid = struct_passwd.pw_gid
                        feature_config['user.gid'] = gid
                except ImportError:
                    pass
                except KeyError:
                    pass

            group = feature_config.get('user.group')
            if group:
                try:
                    import grp  # pylint:disable=import-outside-toplevel
                    struct_group = grp.getgrnam(group)
                    gid = struct_group.gr_id
                    feature_config['user.gid'] = gid
                except ImportError:
                    pass
                except KeyError:
                    pass

    @staticmethod
    def _configure_defaults_user(feature_config):
        uid = feature_config.get('user.uid')
        if uid is None:
            try:
                uid = os.getuid()  # pylint:disable=no-member
            except AttributeError:
                uid = 1000
            feature_config['user.uid'] = uid

        gid = feature_config.get('user.gid')
        if gid is None:
            try:
                gid = os.getgid()  # pylint:disable=no-member
            except AttributeError:
                gid = 1000
            feature_config['user.gid'] = gid
