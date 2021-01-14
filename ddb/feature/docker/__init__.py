# -*- coding: utf-8 -*-
import hashlib
import os
import pathlib
import re
import warnings
from typing import Iterable, ClassVar

import netifaces
from dotty_dict import Dotty
from slugify import slugify

from .actions import EmitDockerComposeConfigAction, DockerComposeBinaryAction, LocalVolumesAction, \
    DockerDisplayInfoAction
from .schema import DockerSchema
from ..feature import Feature, FeatureConfigurationAutoConfigureError
from ..schema import FeatureSchema
from ...action import Action
from ...config import config


class DockerFeature(Feature):
    """
    Docker and docker-compose support.
    """

    @property
    def name(self) -> str:
        return "docker"

    @property
    def dependencies(self) -> Iterable[str]:
        return ["core", "version[optional]"]

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
        self._configure_defaults_user_from_name_and_group(feature_config)
        self._configure_defaults_user(feature_config)
        self._configure_defaults_user_maps(feature_config)
        self._configure_defaults_ip(feature_config)
        self._configure_defaults_debug(feature_config)
        self._configure_defaults_path_mapping(feature_config)
        self._configure_defaults_port_prefix(feature_config)
        self._configure_defaults_compose_project_name(feature_config)
        self._configure_defaults_build_image_tag(feature_config)
        self._configure_defaults_restart_policy(feature_config)
        self._configure_defaults_https(feature_config)

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
    def _configure_defaults_user_maps(feature_config):
        name_to_uid = feature_config.get('user.name_to_uid')
        group_to_gid = feature_config.get('user.group_to_gid')

        try:
            import pwd  # pylint:disable=import-outside-toplevel
            struct_passwds = pwd.getpwall()
            for struct_passwd in struct_passwds:
                name_to_uid[struct_passwd.pw_name] = struct_passwd.pw_uid
                group_to_gid[struct_passwd.pw_name] = struct_passwd.pw_gid
            feature_config['user.name_to_uid'] = name_to_uid
            feature_config['user.group_to_gid'] = group_to_gid
        except ImportError:
            pass

        try:
            import grp  # pylint:disable=import-outside-toplevel
            struct_groups = grp.getgrall()
            for struct_group in struct_groups:
                group_to_gid[struct_group.gr_name] = struct_group.gr_gid
            feature_config['user.group_to_gid'] = group_to_gid
        except ImportError:
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
    def _configure_defaults_debug(feature_config):
        if feature_config.get('debug.host') is None:
            feature_config['debug.host'] = feature_config.get('ip')

        if feature_config.get('debug.disabled') is None:
            if 'core.env.current' in config.data and 'core.env.available' in config.data:
                feature_config['debug.disabled'] = config.data['core.env.current'] != \
                                                   config.data['core.env.available'][-1]
            else:
                feature_config['debug.disabled'] = False

    @staticmethod
    def _configure_defaults_path_mapping(feature_config):
        """
        On windows, this generates a default path mapping matching docker-compose behavior when
        COMPOSE_CONVERT_WINDOWS_PATHS=1 is enabled.

        Drive letter should be lowercased to have the same behavior

        https://github.com/docker/compose/blob/f1059d75edf76e8856469108997c15bb46a41777/compose/config/types.py#L123-L132
        """
        path_mapping = feature_config.get('path_mapping')
        if path_mapping is None:
            path_mapping = {}
            if config.data.get('core.os') == 'nt':
                raw = config.data.get('core.path.project_home')
                mapped = re.sub(r"^([a-zA-Z]):", r"/\1", raw)
                mapped = pathlib.Path(mapped).as_posix()
                mapped = re.sub(r"(\/)(.)(\/.*)", lambda x: x.group(1) + x.group(2).lower() + x.group(3), mapped)
                path_mapping[raw] = mapped
            feature_config['path_mapping'] = path_mapping

    @staticmethod
    def _configure_defaults_port_prefix(feature_config):
        port_prefix = feature_config.get('port_prefix')
        if port_prefix is None:
            project_name = config.data.get('core.project.name')
            if project_name:
                port_prefix = int(hashlib.sha1(project_name.encode('utf-8')).hexdigest(), 16) % 655
                feature_config['port_prefix'] = port_prefix

    @staticmethod
    def _configure_defaults_compose_project_name(feature_config):
        """
        See https://github.com/docker/compose/blob/440c94ea7a7e62b3de50722120ca34c4e818205a/compose/cli/command.py#L181
        """
        compose_project_name = feature_config.get('compose.project_name')

        def normalize_name(name):
            return re.sub(r'[^-_a-z0-9]', '', name.lower())

        if not compose_project_name:
            compose_project_name = os.path.basename(os.path.abspath(config.paths.project_home))

        compose_project_name = normalize_name(compose_project_name)
        feature_config['compose.project_name'] = compose_project_name
        config.env_additions['COMPOSE_PROJECT_NAME'] = compose_project_name

        compose_network_name = feature_config.get('compose.network_name')
        if not compose_network_name:
            compose_network_name = compose_project_name + "_default"

        compose_network_name = normalize_name(compose_network_name)
        feature_config['compose.network_name'] = compose_network_name
        config.env_additions['COMPOSE_NETWORK_NAME'] = compose_network_name + "_default"

    @staticmethod
    def _configure_defaults_build_image_tag(feature_config):
        build_image_tag_from_version = feature_config.get('build_image_tag_from_version')
        if build_image_tag_from_version:
            warnings.warn(
                "docker.build_image_tag_from_version configuration setting is deprecated. "
                "Use docker.build_image_tag_from instead.",
                DeprecationWarning)
        build_image_tag_from = feature_config.get('build_image_tag_from', build_image_tag_from_version)
        build_image_tag = feature_config.get('build_image_tag')
        if build_image_tag is None and build_image_tag_from:
            if isinstance(build_image_tag_from, str):
                tag = config.data.get(build_image_tag_from)
                if tag:
                    build_image_tag = tag
            else:
                # Use tag if we are exactly on a tag, branch otherwise
                tag = config.data.get('version.tag')
                version = config.data.get('version.version')
                branch = config.data.get('version.branch')
                if tag and version and tag == version:
                    build_image_tag = tag
                elif branch:
                    build_image_tag = branch
            if build_image_tag:
                feature_config['build_image_tag'] = slugify(build_image_tag, regex_pattern=r'[^\w][^\w.-]{0,127}')

    @staticmethod
    def _configure_defaults_restart_policy(feature_config):
        restart_policy = feature_config.get('restart_policy')
        if restart_policy is None:
            if config.data.get("core.env.current") == "dev":
                feature_config['restart_policy'] = 'no'
            else:
                feature_config['restart_policy'] = 'unless-stopped'

    @staticmethod
    def _configure_defaults_https(feature_config):
        https = feature_config.get('reverse_proxy.https')
        redirect_to_https = feature_config.get('reverse_proxy.redirect_to_https')

        if redirect_to_https and not https:
            feature_config['reverse_proxy.redirect_to_https'] = False
