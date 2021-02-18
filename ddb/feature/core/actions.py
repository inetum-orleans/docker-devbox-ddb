# -*- coding: utf-8 -*-
import os
import platform
import re
import shutil
import sys
from datetime import date
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Optional
from urllib.error import HTTPError

import distro
import requests
import yaml
from dotty_dict import Dotty
from progress.bar import IncrementalBar
from semver import VersionInfo

from ddb import __version__
from ddb.action import Action, InitializableAction
from ddb.cache import caches, register_global_cache
from ddb.config import config
from ddb.event import events
from ddb.utils.file import force_remove
from ddb.utils.table_display import get_table_display
from .. import features
from ...action.action import EventBinding
from ...action.runner import FailFastError, ExpectedError
from ...command import Command
from ...config.flatten import flatten
from ...context import context


def get_latest_release_version(github_repository: str):
    """
    Retrieve latest release version from GitHub API
    :param github_repository github repository to check
    :return: Version from tag_name retrieved from GitHub API
    """
    response = requests.get('https://api.github.com/repos/{}/releases/latest'.format(github_repository))
    try:
        response.raise_for_status()
        tag_name = response.json().get('tag_name')
        if tag_name and tag_name.startswith('v'):
            tag_name = tag_name[1:]
        return tag_name
    except HTTPError:  # pylint:disable=bare-except
        return None


def get_current_version():
    """
    Get the current version
    :return:
    """
    return __version__


def print_version(github_repository, silent=False):
    """
    Print the version and informations.
    :return:
    """
    if silent:
        print(get_current_version())
        return

    blocks = []
    header_block = ['ddb ' + get_current_version()]
    blocks.append(header_block)

    last_release = get_latest_release_version(github_repository)

    if last_release and get_current_version() < last_release:
        blocks.append(_build_update_header(last_release))
        blocks.append(_build_update_details(github_repository, last_release))
    blocks.append([
        'Please report any bug or feature request at',
        'https://github.com/inetum-orleans/docker-devbox-ddb/issues'
    ])
    print(get_table_display(blocks))


_version_re = re.compile(
    r"""[vV]?
        (?P<major>0|[1-9]\d*)
        (\.
        (?P<minor>0|[1-9]\d*)
        (\.
            (?P<patch>0|[1-9]\d*)
        )?
        )?
    """,
    re.VERBOSE,
)


def coerce_version(version):
    """
    Convert an incomplete version string into a semver-compatible VersionInfo
    object

    * Tries to detect a "basic" version string (``major.minor.patch``).
    * If not enough components can be found, missing components are
        set to zero to obtain a valid semver version.

    :param str version: the version string to convert
    :return: a tuple with a :class:`VersionInfo` instance (or ``None``
        if it's not a version) and the rest of the string which doesn't
        belong to a basic version.
    :rtype: tuple(:class:`VersionInfo` | None, str)
    """
    match = _version_re.search(version)
    if not match:
        return None, version

    ver = {
        key: 0 if value is None else value for key, value in match.groupdict().items()
    }

    ver = VersionInfo(**ver)
    rest = match.string[match.end():]
    return ver, rest


def is_version_greater(reference, version):
    """
    Check if version is greater than reference.
    :param reference:
    :param version:
    :return:
    """
    return coerce_version(reference) < coerce_version(version)


def is_version_greater_or_equal(reference, version):
    """
    Check if version is greater or equal than reference.
    :param reference:
    :param version:
    :return:
    """
    return coerce_version(reference) < coerce_version(version)


def check_for_update(github_repository: str, output=False, details=False):
    """
    Check if a new version is available on github.
    :param github_repository github repository to check
    :param output: if True, new version information will be displayed.
    :param details: if True, will display more details.
    :return: Version of the latest release if it doesn't match the current one.
    """
    last_release = get_latest_release_version(github_repository)

    if last_release and is_version_greater(get_current_version(), last_release):
        if output:
            blocks = [_build_update_header(last_release)]
            if details:
                row = _build_update_details(github_repository, last_release)
                blocks.append(row)
                print(get_table_display(blocks))
            else:
                for block in blocks:
                    for row in block:
                        print(row)
        return last_release
    return None


def _build_update_header(last_release):
    return ['A new version is available: {}'.format(last_release)]


def _build_update_details(github_repository, last_release):
    row = []
    update_tip = _build_update_tip()
    if update_tip:
        row.append(update_tip)
    row.extend((
        'For more information, check the following links:',
        'https://github.com/{}/releases/tag/{}'.format(github_repository, last_release),
        'https://github.com/{}/releases/tag/{}/CHANGELOG.md'.format(github_repository, last_release),
    ))
    return row


def _build_update_tip():
    if is_binary():
        return 'run "ddb self-update" command to update.'
    return ''


def is_binary():
    """
    Check if current process is binary.
    :return:
    """
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')


def get_binary_path():
    """
    Get the binary path
    :return:
    """
    if config.cwd:
        return os.path.join(config.cwd, sys.argv[0])
    return sys.argv[0]


def get_binary_destination_path(binary_path: str):
    """
    Get binary path destination
    :param binary_path:
    :return:
    """
    if binary_path.endswith('.py') \
            and Path(binary_path).read_text().startswith("#!/usr/bin/env python"):
        # Avoid removing main source file when running on development.
        binary_path = binary_path[:-3] + ".bin"

    for qualifier in ['-linux', '-alpine', '-macos', '-windows']:
        binary_path = binary_path.replace(qualifier, '')
    return binary_path


def get_binary_remote_name():
    """
    Get binary remote name
    :return:
    """
    if platform.system() == 'Windows':
        return 'ddb-windows.exe'
    if platform.system() == 'Darwin':
        return 'ddb-macos'
    if platform.system() == 'Linux':
        if distro.id() == 'alpine':
            return 'ddb-alpine'
        return 'ddb-linux'
    return None


class FeaturesAction(Action):
    """
    Display all features
    """

    @property
    def event_bindings(self):
        return events.phase.features

    @property
    def name(self) -> str:
        return "core:features"

    @staticmethod
    def execute():
        """
        Execute action
        """
        enabled_features = [f for f in features.all() if not f.disabled]

        for feature in enabled_features:
            print("%s: %s" % (feature.name, feature.description))


class ConfigAction(Action):
    """
    Dump configuration
    """

    @property
    def event_bindings(self):
        return events.phase.config

    @property
    def name(self) -> str:
        return "core:config"

    @staticmethod
    def execute():
        """
        Execute action
        """
        configuration, configuration_files = ConfigAction._get_configuration_files(
            config.args.full, config.args.files
        )

        if config.args.property:
            configuration, configuration_files = ConfigAction._handle_property(configuration, configuration_files)

        if config.args.value:
            return ConfigAction._print_config_value(configuration, config.args.property)

        if config.args.variables:
            return ConfigAction._print_config_variables(configuration, configuration_files)

        return ConfigAction._print_config_yaml(configuration, configuration_files)

    @staticmethod
    def _handle_property(configuration, configuration_files):
        configuration, configuration_files = ConfigAction._get_configurations_for_prop(
            config.args.property,
            configuration,
            configuration_files
        )
        if configuration is None and not config.args.full:
            configuration, configuration_files = ConfigAction._get_configuration_files(
                True, config.args.files
            )

            configuration, configuration_files = ConfigAction._get_configurations_for_prop(
                config.args.property,
                configuration,
                configuration_files
            )
        if configuration is not None:
            root_config = Dotty({})
            root_config[config.args.property] = configuration
            configuration = dict(root_config)
        if configuration_files:
            root_configuration_files = {}
            for k, configuration_file in configuration_files.items():
                root_configuration_file = Dotty({})
                root_configuration_file[config.args.property] = configuration_file
                root_configuration_files[k] = dict(root_configuration_file)
            configuration_files = root_configuration_files
        return configuration, configuration_files

    @staticmethod
    def _print_config_yaml(configuration, configuration_files):
        if config.args.files and configuration_files:
            for file, configuration_file in configuration_files.items():
                print(f"--- # {file}")
                print(yaml.safe_dump(configuration_file))
        else:
            if isinstance(configuration, (dict, list)):
                print(yaml.safe_dump(configuration))
            elif configuration is not None:
                print(configuration)

    @staticmethod
    def _print_config_variables(configuration, configuration_files):
        if config.args.files and configuration_files:
            for index, (file, configuration_file) in enumerate(configuration_files.items()):
                if index > 0:
                    print()
                print(f"# {file}")
                flat = flatten(Dotty(configuration_file), keep_primitive_list=True)
                for key in sorted(flat.keys()):
                    print(f"{key}: {flat[key]}")
        else:
            flat = flatten(Dotty(configuration), keep_primitive_list=True)
            for key in sorted(flat.keys()):
                print(f"{key}: {flat[key]}")

    @staticmethod
    def _print_config_value(configuration, prop):
        if configuration is None:
            raise ValueError(f"{prop} not found in configuration.")
        dotty_configuration = Dotty(configuration)
        if prop and prop not in dotty_configuration:
            raise ValueError(f"{prop} not found in configuration.")
        value = dotty_configuration[prop] if prop and prop in dotty_configuration else configuration
        print(value)

    @staticmethod
    def _get_configurations_for_prop(prop, configuration, configuration_files):
        prop_configuration = Dotty(configuration).get(prop)

        if configuration_files:
            prop_configuration_files = {}
            for file, configuration_file in configuration_files.items():
                prop_configuration_file = Dotty(configuration_file).get(prop)
                if prop_configuration_file:
                    prop_configuration_files[file] = prop_configuration_file
        else:
            prop_configuration_files = configuration_files

        return prop_configuration, prop_configuration_files

    @staticmethod
    def _prune_default_configuration(default_configuration, flat_file_configuration):
        for file_key in flat_file_configuration.values():
            if file_key in default_configuration:
                default_configuration.pop(file_key, None)
                parent_k = file_key
                while '.' in parent_k:
                    (parent_k, _) = parent_k.rsplit('.', 1)
                    parent_value = default_configuration.get(parent_k)
                    if parent_value is None or not parent_value:
                        default_configuration.pop(parent_k, None)
                    else:
                        break

    @staticmethod
    def _get_configuration_files(full, files):
        default_configuration = dict(config.data.copy())

        if full and not files:
            configuration_files = None
            return default_configuration, configuration_files

        configuration, configuration_files = config.read()
        if full:
            for file_configuration in configuration_files.values():
                flat_file_configuration = flatten(file_configuration)
                ConfigAction._prune_default_configuration(default_configuration, flat_file_configuration)

            tmp = {'default': default_configuration}
            tmp.update(configuration_files)
            configuration_files = tmp
        return configuration, configuration_files


class EjectAction(Action):
    """
    Dump configuration
    """

    @property
    def event_bindings(self):
        def eject_processor(source: Optional[str], target: str):
            if not source or not \
                    os.path.abspath(source).startswith(config.paths.project_home):
                return False
            return (), {"source": source, "target": target}

        return (
            EventBinding(events.file.generated, self.delete_generated_source, eject_processor)
        )

    @property
    def name(self) -> str:
        return "core:eject"

    @property
    def order(self):
        return 1024 * 1024

    @property
    def disabled(self) -> bool:
        if not config.eject:
            return True
        return super().disabled

    @staticmethod
    def delete_generated_source(source: Optional[str], target: str):
        """
        Execute action
        """
        force_remove(source)
        events.file.deleted(source)
        events.file.deleted(target)


class ReloadConfigAction(Action):
    """
    In watch mode, reload config if one configuration file is changed.
    """

    @property
    def event_bindings(self):
        def config_file_processor(file: str):
            if os.path.abspath(file) in config.files:
                return (), {"file": file}
            return None

        return (
            EventBinding(events.file.found, self.execute, config_file_processor)
        )

    @property
    def disabled(self) -> bool:
        return 'watch' not in config.args or not config.args.watch

    @property
    def name(self) -> str:
        return "core:reload-config"

    @staticmethod
    def execute(file: str):
        """
        Execute action
        """
        if context.watching:
            data, _ = config.read()
            try:
                context.log.info("Configuration file has changed.")
                config.clear()
                config.load_from_data(data)
                all_features = features.all()
                for feature in all_features:
                    feature.configure()
                context.log.info("Configuration has been reloaded.")
                events.config.reloaded()
            except Exception as exc:  # pylint:disable=broad-except
                context.log.warning("Configuration has fail to reload: %s", str(exc))
                return


class VersionAction(Action):
    """
    Display display version information when --version flag is used.
    """

    @property
    def name(self) -> str:
        return "core:version"

    @property
    def event_bindings(self):
        return events.main.version

    @staticmethod
    def execute(silent: bool):
        """
        Check for updates
        :param command command name
        :return:
        """
        github_repository = config.data.get('core.github_repository')
        print_version(github_repository, silent)


class CheckForUpdateAction(InitializableAction):
    """
    Check if a new version is available on github.
    """

    def initialize(self):
        register_global_cache('core.check_for_update.version')

    @property
    def name(self) -> str:
        return "core:check-for-update"

    @property
    def event_bindings(self):
        return events.main.terminate

    @staticmethod
    def execute(command: Command):
        """
        Check for updates
        :param command command name
        :return:
        """
        if not command.avoid_stdout and config.data.get('core.check_updates'):
            cache = caches.get('core.check_for_update.version')
            last_check = cache.get('last_check', None)
            today = date.today()

            if last_check is None or last_check < today:
                github_repository = config.data.get('core.github_repository')
                check_for_update(github_repository, True, True)

            cache.set('last_check', today)


class RequiredVersionError(FailFastError, ExpectedError):
    """
    Exception that should be raised when the current version doesn't fullfil the required one.
    """

    def log_error(self):
        context.log.error(str(self))


class CheckRequiredVersion(Action):
    """
    Check if a new version is available on github.
    """

    @property
    def name(self) -> str:
        return "core:check-required-version"

    @property
    def event_bindings(self):
        return events.main.start

    @staticmethod
    def execute(command: Command):
        """
        Check for updates
        :param command command name
        :return:
        """
        if command.name not in ['self-update']:
            required_version = config.data.get('core.required_version')
            if not required_version:
                return
            if is_version_greater_or_equal(get_current_version(), required_version):
                update_tip = _build_update_tip()
                if update_tip:
                    update_tip = ' ' + update_tip
                raise RequiredVersionError(
                    "This project requires ddb {}+. Current version is {}.{}".format(required_version,
                                                                                     get_current_version(),
                                                                                     update_tip))


class SelfUpdateAction(Action):
    """
    Self update ddb if a newer version is available.
    """

    @property
    def name(self) -> str:
        return "core:selfupdate"

    @property
    def event_bindings(self):
        return events.phase.selfupdate

    def execute(self):
        """
        Execute action
        """
        github_repository = config.data.get('core.github_repository')

        if not is_binary():
            print('ddb is running from a package mode than doesn\'t support self-update.')
            print(
                'You can download binary package supporting it ' +
                'from github: https://github.com/{}/releases'.format(github_repository)
            )
            return

        last_release = check_for_update(github_repository, True)
        if not last_release:
            print('ddb is already up to date.')
            if 'force' not in config.args or not config.args.force:
                return

        if not last_release:
            last_release = get_latest_release_version(github_repository)

        self.self_update_binary(github_repository, last_release)

    @staticmethod
    def self_update_binary(github_repository, version):
        """
        Self update the ddb binary
        :param github_repository:
        :param version:
        :return:
        """
        binary_path = get_binary_path()

        if not os.access(binary_path, os.W_OK):
            raise PermissionError(f"You don't have permission to write on ddb binary file. ({binary_path})")

        remote_filename = get_binary_remote_name()
        if not remote_filename:
            print('ddb is running from a platform that doesn\'t support binary package mode.')
            return

        url = 'https://github.com/{}/releases/download/v{}/{}'.format(github_repository, version, remote_filename)

        progress_bar = None
        with requests.get(url, stream=True) as response:
            response.raise_for_status()

            tmp = NamedTemporaryFile(delete=False)
            try:
                if not progress_bar:
                    content_length = int(response.headers['content-length'])
                    progress_bar = IncrementalBar('Downloading', max=content_length, suffix='%(percent)d%%')

                for chunk in response.iter_content(32 * 1024):
                    progress_bar.next(len(chunk))  # pylint:disable=not-callable
                    tmp.write(chunk)
                tmp.flush()
            finally:
                tmp.close()

            binary_path = get_binary_destination_path(binary_path)
            shutil.copymode(binary_path, tmp.name)
            force_remove(binary_path)  # This is required on windows
            os.rename(tmp.name, binary_path)

            progress_bar.finish()

        config.data['core.check_updates'] = False
        print("ddb has been updated.")
