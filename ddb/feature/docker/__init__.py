# -*- coding: utf-8 -*-
import os
import re
from typing import Iterable, ClassVar

from dotty_dict import dotty
import netifaces

from .schema import DockerSchema
from ..feature import Feature, FeatureConfigurationAutoConfigureError
from ..schema import FeatureSchema
from ...action import Action


class DockerFeature(Feature):
    """
    Docker/Docker Compose integration
    """

    @property
    def name(self) -> str:
        return "docker"

    @property
    def schema(self) -> ClassVar[FeatureSchema]:
        return DockerSchema

    @property
    def actions(self) -> Iterable[Action]:
        return ()

    def _auto_configure(self, feature_config: dict):
        feature_config = dotty(feature_config)

        uid = feature_config.get('user.uid')
        if uid is None:
            try:
                uid = os.getuid()  # pylint:disable=no-member
                feature_config['user.uid'] = uid
            except Exception as error:
                raise FeatureConfigurationAutoConfigureError(self, 'user.uid', error)

        gid = feature_config.get('user.gid')
        if gid is None:
            try:
                gid = os.getgid()  # pylint:disable=no-member
                feature_config['user.gid'] = gid
            except Exception as error:
                raise FeatureConfigurationAutoConfigureError(self, 'user.gid', error)

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
        # TODO: Export configuration to environment for docker/docker-compose to have those variables available
