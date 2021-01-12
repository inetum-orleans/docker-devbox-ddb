# -*- coding: utf-8 -*-
import hashlib
import os
import pathlib
import re
from typing import ClassVar, Iterable

from dotty_dict import Dotty
from slugify import slugify

from ddb.action import Action
from ddb.feature import Feature
from .actions import JsonnetAction
from .schema import JsonnetSchema
from ...config import config
from ...utils.file import TemplateFinder


class JsonnetFeature(Feature):
    """
    Render template files with Jsonnet (https://jsonnet.org).
    """

    @property
    def name(self) -> str:
        return "jsonnet"

    @property
    def dependencies(self) -> Iterable[str]:
        return ["core", "file", "docker[optional]", "version[optional]"]

    @property
    def schema(self) -> ClassVar[JsonnetSchema]:
        return JsonnetSchema

    @property
    def actions(self) -> Iterable[Action]:
        return (
            JsonnetAction(),
        )

    def _configure_defaults(self, feature_config: Dotty):
        self._configure_defaults_includes(feature_config)
        self._configure_defaults_user_from_name_and_group(feature_config)
        self._configure_defaults_user(feature_config)
        self._configure_defaults_user_maps(feature_config)
        self._configure_defaults_xdebug(feature_config)
        self._configure_defaults_path_mapping(feature_config)
        self._configure_defaults_port_prefix(feature_config)
        self._configure_defaults_compose_project_name(feature_config)
        self._configure_defaults_build_image_tag(feature_config)
        self._configure_defaults_restart_policy(feature_config)
        self._configure_defaults_https(feature_config)

    @staticmethod
    def _configure_defaults_includes(feature_config):
        includes = feature_config.get("includes")
        if includes is None:
            includes = TemplateFinder.build_default_includes_from_suffixes(
                feature_config["suffixes"],
                feature_config["extensions"]
            )
            feature_config["includes"] = includes

    @staticmethod
    def _configure_defaults_user_from_name_and_group(feature_config):
        uid = feature_config.get('docker.user.uid', config.data.get('docker.user.uid'))
        gid = feature_config.get('docker.user.gid', config.data.get('docker.user.gid'))

        if uid is None or gid is None:
            name = feature_config.get('docker.user.name')
            if name:
                try:
                    import pwd  # pylint:disable=import-outside-toplevel
                    struct_passwd = pwd.getpwnam(name)
                    if uid is None:
                        uid = struct_passwd.pw_uid
                        feature_config['docker.user.uid'] = uid
                    if gid is None:
                        gid = struct_passwd.pw_gid
                        feature_config['docker.user.gid'] = gid
                except ImportError:
                    pass
                except KeyError:
                    pass

            group = feature_config.get('docker.user.group')
            if group:
                try:
                    import grp  # pylint:disable=import-outside-toplevel
                    struct_group = grp.getgrnam(group)
                    gid = struct_group.gr_id
                    feature_config['docker.user.gid'] = gid
                except ImportError:
                    pass
                except KeyError:
                    pass

    @staticmethod
    def _configure_defaults_user_maps(feature_config):
        name_to_uid = feature_config.get('docker.user.name_to_uid')
        group_to_gid = feature_config.get('docker.user.group_to_gid')

        try:
            import pwd  # pylint:disable=import-outside-toplevel
            struct_passwds = pwd.getpwall()
            for struct_passwd in struct_passwds:
                name_to_uid[struct_passwd.pw_name] = struct_passwd.pw_uid
                group_to_gid[struct_passwd.pw_name] = struct_passwd.pw_gid
            feature_config['docker.user.name_to_uid'] = name_to_uid
            feature_config['docker.user.group_to_gid'] = group_to_gid
        except ImportError:
            pass

        try:
            import grp  # pylint:disable=import-outside-toplevel
            struct_groups = grp.getgrall()
            for struct_group in struct_groups:
                group_to_gid[struct_group.gr_name] = struct_group.gr_gid
            feature_config['docker.user.group_to_gid'] = group_to_gid
        except ImportError:
            pass

    @staticmethod
    def _configure_defaults_user(feature_config):
        uid = feature_config.get('docker.user.uid', config.data.get('docker.user.uid'))
        if uid is None:
            try:
                uid = os.getuid()  # pylint:disable=no-member
            except AttributeError:
                uid = 1000
            feature_config['docker.user.uid'] = uid

        gid = feature_config.get('docker.user.gid', config.data.get('docker.user.gid'))
        if gid is None:
            try:
                gid = os.getgid()  # pylint:disable=no-member
            except AttributeError:
                gid = 1000
            feature_config['docker.user.gid'] = gid

    @staticmethod
    def _configure_defaults_xdebug(feature_config):
        if feature_config.get('docker.xdebug.host') is None:
            feature_config['docker.xdebug.host'] = config.data.get('docker.ip')

        if feature_config.get('docker.xdebug.session') is None:
            feature_config['docker.xdebug.session'] = config.data.get('core.project.name')

        if not feature_config.get('docker.xdebug.disabled'):
            if feature_config['docker.xdebug.host'] is None:
                feature_config['docker.xdebug.disabled'] = True

            if 'core.env.current' in config.data and 'core.env.available' in config.data:
                feature_config['docker.xdebug.disabled'] = config.data['core.env.current'] != \
                                                           config.data['core.env.available'][-1]
            else:
                feature_config['docker.xdebug.disabled'] = False

    @staticmethod
    def _configure_defaults_path_mapping(feature_config):
        """
        On windows, this generates a default path mapping matching docker-compose behavior when
        COMPOSE_CONVERT_WINDOWS_PATHS=1 is enabled.

        Drive letter should be lowercased to have the same behavior

        https://github.com/docker/compose/blob/f1059d75edf76e8856469108997c15bb46a41777/compose/config/types.py#L123-L132
        """
        path_mapping = feature_config.get('docker.path_mapping')
        if path_mapping is None:
            path_mapping = {}
            if config.data.get('core.os') == 'nt':
                raw = config.data.get('core.path.project_home')
                mapped = re.sub(r"^([a-zA-Z]):", r"/\1", raw)
                mapped = pathlib.Path(mapped).as_posix()
                mapped = re.sub(r"(\/)(.)(\/.*)", lambda x: x.group(1) + x.group(2).lower() + x.group(3), mapped)
                path_mapping[raw] = mapped
            feature_config['docker.path_mapping'] = path_mapping

    @staticmethod
    def _configure_defaults_port_prefix(feature_config):
        port_prefix = feature_config.get('docker.expose.port_prefix')
        if port_prefix is None:
            project_name = config.data.get('core.project.name')
            if project_name:
                port_prefix = int(hashlib.sha1(project_name.encode('utf-8')).hexdigest(), 16) % 655
                feature_config['docker.expose.port_prefix'] = port_prefix

    @staticmethod
    def _configure_defaults_compose_project_name(feature_config):
        """
        See https://github.com/docker/compose/blob/440c94ea7a7e62b3de50722120ca34c4e818205a/compose/cli/command.py#L181
        """
        compose_project_name = feature_config.get('docker.compose.project_name')
        if compose_project_name is None:
            compose_project_name = feature_config.get('core.project.name')

        def normalize_name(name):
            return re.sub(r'[^-_a-z0-9]', '', name.lower())

        if not compose_project_name:
            compose_project_name = os.path.basename(os.path.abspath(config.paths.project_home))

        compose_project_name = normalize_name(compose_project_name)
        feature_config['docker.compose.project_name'] = compose_project_name
        config.env_additions['COMPOSE_PROJECT_NAME'] = compose_project_name

        compose_network_name = feature_config.get('docker.compose.network_name')
        if not compose_network_name:
            compose_network_name = compose_project_name + "_default"

        compose_network_name = normalize_name(compose_network_name)
        feature_config['docker.compose.network_name'] = compose_network_name
        config.env_additions['COMPOSE_NETWORK_NAME'] = compose_network_name + "_default"

    @staticmethod
    def _configure_defaults_build_image_tag(feature_config):
        build_image_tag_from = feature_config.get('docker.build.image_tag_from')
        build_image_tag = feature_config.get('docker.builder.image_tag')
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
                feature_config['docker.build.image_tag'] = slugify(build_image_tag,
                                                                   regex_pattern=r'[^\w][^\w.-]{0,127}')

    @staticmethod
    def _configure_defaults_restart_policy(feature_config):
        restart_policy = feature_config.get('docker.service.restart')
        if restart_policy is None:
            if config.data.get("core.env.current") == "dev":
                feature_config['docker.service.restart'] = 'no'
            else:
                feature_config['docker.service.restart'] = 'unless-stopped'

    @staticmethod
    def _configure_defaults_https(feature_config):
        https = feature_config.get('docker.virtualhost.https')
        redirect_to_https = feature_config.get('docker.virtualhost.redirect_to_https')

        if redirect_to_https and not https:
            feature_config['docker.virtualhost.redirect_to_https'] = False
