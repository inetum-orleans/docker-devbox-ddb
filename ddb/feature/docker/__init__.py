# -*- coding: utf-8 -*-
import os
import re
from typing import Iterable, ClassVar

import netifaces
import pathlib
from dotty_dict import Dotty

from .actions import EmitDockerComposeConfigAction
from .schema import DockerSchema
from ..feature import Feature, FeatureConfigurationAutoConfigureError
from ..schema import FeatureSchema
from ...action import Action
from ...config import config


class DockerFeature(Feature):
    """
    Docker/Docker Compose integration
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
        )

    def _configure_defaults(self, feature_config: Dotty):
        self._configure_defaults_user(feature_config)
        self._configure_defaults_ip(feature_config)
        self._configure_defaults_registry(feature_config)
        self._configure_defaults_path_mapping(feature_config)

    def _configure_defaults_user(self, feature_config):
        uid = feature_config.get('user.uid')
        if uid is None:
            try:
                uid = os.getuid()  # pylint:disable=no-member
            except AttributeError as error:
                raise FeatureConfigurationAutoConfigureError(self, 'user.uid', error)
            feature_config['user.uid'] = uid

        gid = feature_config.get('user.gid')
        if gid is None:
            try:
                gid = os.getgid()  # pylint:disable=no-member
            except AttributeError as error:
                raise FeatureConfigurationAutoConfigureError(self, 'user.gid', error)
            feature_config['user.gid'] = gid

    def _configure_defaults_ip(self, feature_config):
        ip_address = feature_config.get('ip')
        if not ip_address:
            docker_host = os.environ.get('DOCKER_HOST')
            if docker_host:
                ip_match = re.match(r"(?:.*?)://(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*", docker_host)
                if ip_match:
                    ip_address = ip_match.group(1)

        if not ip_address:
            interface = feature_config.get('interface')
            try:
                docker_if = netifaces.ifaddresses(interface)
            except ValueError:
                raise FeatureConfigurationAutoConfigureError(self, 'ip',
                                                             "Invalid network interface: " + interface)
            if docker_if and netifaces.AF_INET in docker_if:
                docker_af_inet = docker_if[netifaces.AF_INET][0]
                ip_address = docker_af_inet['addr']
            else:
                raise FeatureConfigurationAutoConfigureError(self, 'ip',
                                                             "Can't get ip address "
                                                             "from network interface configuration: " + interface)

        feature_config['ip'] = ip_address

    @staticmethod
    def _configure_defaults_path_mapping(feature_config):
        path_mapping = feature_config.get('path_mapping')
        if path_mapping is None:
            path_mapping = {}
            if config.data.get('core.os') == 'nt':
                raw = config.data.get('core.path.project_home')
                mapped = re.sub(r"^([a-zA-Z]):", r"/\1", raw)
                mapped = pathlib.Path(mapped).as_posix()
                path_mapping[raw] = mapped
            feature_config['path_mapping'] = path_mapping

    @staticmethod
    def _configure_defaults_registry(feature_config):
        registry_name = feature_config.get('registry.name')
        if registry_name and not registry_name.endswith('/'):
            registry_name += '/'
            feature_config['registry.name'] = registry_name

        registry_repository = feature_config.get('registry.repository')
        if registry_repository and not registry_repository.endswith('/'):
            registry_repository += '/'
            feature_config['registry.repository'] = registry_repository
