#!/usr/bin/env python
# -*- coding: utf-8 -*-
import inspect
import logging
import os
import sys
import threading
from argparse import ArgumentParser, Namespace
from datetime import date
from gettext import gettext as _
from importlib import import_module
from typing import Optional, Sequence, Iterable, Callable, Union, List

import pkg_resources
import verboselogs
from colorlog import default_log_colors, ColoredFormatter
from toposort import toposort_flatten

from ddb import __version__
from ddb.action import actions
from ddb.action.action import EventBinding, Action, WatchSupport
from ddb.action.runnerfactory import action_event_binding_runner_factory
from ddb.binary import binaries
from ddb.cache import caches, global_cache_name, requests_cache_name, \
    project_binary_cache_name, register_global_cache, project_cache_name
from ddb.cache import register_project_cache
from ddb.command import commands
from ddb.command.command import execute_command, Command
from ddb.config import config
from ddb.context import context
from ddb.event import bus
from ddb.feature import features, Feature
from ddb.feature.certs import CertsFeature
from ddb.feature.copy import CopyFeature
from ddb.feature.core import CoreFeature
from ddb.feature.docker import DockerFeature
from ddb.feature.file import FileFeature
from ddb.feature.fixuid import FixuidFeature
from ddb.feature.git import GitFeature
from ddb.feature.gitignore import GitignoreFeature
from ddb.feature.jinja import JinjaFeature
from ddb.feature.jsonnet import JsonnetFeature
from ddb.feature.permissions import PermissionsFeature
from ddb.feature.run import RunFeature
from ddb.feature.shell import ShellFeature
from ddb.feature.smartcd import SmartcdFeature
from ddb.feature.symlinks import SymlinksFeature
from ddb.feature.traefik import TraefikFeature
from ddb.feature.version import VersionFeature
from ddb.feature.ytt import YttFeature
from ddb.phase import phases
from ddb.registry import Registry, RegistryObject
from ddb.service import services
from ddb.utils.release import ddb_repository, get_lastest_release_version
from ddb.utils.table_display import get_table_display

_default_available_features = [CertsFeature(),
                               CopyFeature(),
                               CoreFeature(),
                               DockerFeature(),
                               FileFeature(),
                               FixuidFeature(),
                               GitFeature(),
                               GitignoreFeature(),
                               JinjaFeature(),
                               JsonnetFeature(),
                               PermissionsFeature(),
                               RunFeature(),
                               SmartcdFeature(),
                               ShellFeature(),
                               SymlinksFeature(),
                               TraefikFeature(),
                               VersionFeature(),
                               YttFeature()]

_available_features = list(_default_available_features)


def load_plugins():
    """Load plugins"""
    for directory in [d for d in config.paths if d]:
        extension_directory = os.path.join(directory, ".ddb")
        if os.path.exists(extension_directory):
            sys.path.append(os.path.abspath(extension_directory))
            for dirpath, _, files in os.walk(extension_directory):
                module_name = os.path.relpath(dirpath, extension_directory).replace(os.sep, ".")
                if module_name == '.':
                    module_name = None

                for file in files:
                    if file == "__init__.py":
                        _load_plugins_module(module_name)
                    elif file.endswith("py"):
                        file_module_name = os.path.splitext(file)[0]
                        _load_plugins_module(
                            file_module_name if not module_name else '.'.join((module_name, file_module_name)))


def _load_plugins_module(module_name):
    if not module_name:
        return
    module = import_module(module_name)
    for _, clazz in inspect.getmembers(module):
        if inspect.isclass(clazz) and \
                clazz.__module__ == module.__name__ and \
                not clazz.__name__.startswith("_") and \
                issubclass(clazz, Feature):
            feature = clazz()
            _available_features.append(feature)


def register_features(to_register: Iterable[Feature] = None):
    """
    Register default features and setuptools entrypoint 'ddb_features' inside features registry.
    Features are registered in order for their dependency to be registered first with a topological sort.
    Withing a command phase, actions are executed in the order of their feature registration.
    """
    if to_register is None:
        to_register = _available_features

    entrypoint_features = {f.name: f for f in to_register}
    for entry_point in pkg_resources.iter_entry_points('ddb_features'):
        feature = entry_point.load()()
        entrypoint_features[feature.name] = feature

    required_dependencies, toposort_data = _prepare_dependencies_data(entrypoint_features)
    _check_missing_dependencies(entrypoint_features, required_dependencies)

    dependencies = config.data.get('dependencies')
    if dependencies:
        for feat, feat_dependencies in dependencies.items():
            if feat not in toposort_data:
                toposort_data[feat] = set()
            for feat_dependency in feat_dependencies:
                toposort_data[feat].add(feat_dependency)

    sorted_feature_names = toposort_flatten(toposort_data, sort=True)
    for feature_name in sorted_feature_names:
        feature = entrypoint_features.get(feature_name)
        if feature:
            features.register(feature)


def _prepare_dependencies_data(entrypoint_features):
    """
    Compute required dependencies and toposort data.
    """
    required_dependencies = {}
    toposort_data = {}
    for name, feat in entrypoint_features.items():
        feat_required_dependencies = []
        dependencies = set()
        for dependency_item in feat.dependencies:
            if not dependency_item.endswith('[optional]'):
                feat_required_dependencies.append(dependency_item)
            else:
                dependency_item = dependency_item[0:len(dependency_item) - len('[optional]')]
            dependencies.add(dependency_item)

        toposort_data[name] = dependencies
        required_dependencies[name] = feat_required_dependencies
    return required_dependencies, toposort_data


def _check_missing_dependencies(entrypoint_features, required_dependencies):
    """
    Check missing required dependencies
    """
    for name, feat_required_dependencies in required_dependencies.items():
        for required_dependency in feat_required_dependencies:
            if required_dependency not in entrypoint_features.keys():
                raise ValueError("A required dependency is missing for " +
                                 name + " feature (" + required_dependency + ")")


def prepare_project_home():
    """
    Set working directory to project home.
    """
    if config.paths.project_home:
        os.chdir(config.paths.project_home)


def register_default_caches():
    """
    Register default caches.
    """
    register_project_cache(project_cache_name)
    binaries.set_cache(register_project_cache(project_binary_cache_name))
    register_global_cache(global_cache_name)
    register_global_cache(requests_cache_name)


def register_objects(features_list: Iterable[Feature],
                     objects_getter: Callable[[Feature], Iterable[RegistryObject]],
                     registry: Registry[RegistryObject]):
    """
    Register objects from features inside registry.
    """
    all_objects = []

    for feature in features_list:
        objects = objects_getter(feature)
        all_objects.extend(objects)

    for obj in all_objects:
        registry.register(obj)


def load_registered_features():
    """
    Load all registered features.
    """
    all_features = features.all()

    for feature in all_features:
        feature.before_load()

    for feature in all_features:
        feature.configure()

    enabled_features = [f for f in all_features if not f.disabled]  # type: Iterable[Feature]

    register_objects(enabled_features, lambda f: f.phases, phases)
    register_objects(enabled_features, lambda f: f.commands, commands)
    register_objects(enabled_features, lambda f: [a for a in f.actions if not a.disabled], actions)
    register_objects(enabled_features, lambda f: f.binaries, binaries)
    register_objects(enabled_features, lambda f: f.services, services)

    for feature in enabled_features:
        feature.after_load()

    return enabled_features


def configure_logging(level: Union[str, int] = logging.INFO):
    """
    Configure context logger.
    """
    verboselogs.install()

    log_colors = dict(default_log_colors)
    log_colors['NOTICE'] = 'thin_white'
    log_colors['VERBOSE'] = 'thin_white'
    log_colors['DEBUG'] = 'thin_cyan'
    log_colors['SUCCESS'] = 'bold_green'
    log_colors['SPAM'] = 'bold_red'

    class CustomFormatter(ColoredFormatter):
        """
        Custom context logger formatter.
        """

        def format(self, record):
            record.simplename = record.name.rsplit(".", 1)[-1]
            return super().format(record)

    handler = logging.StreamHandler()
    handler.setFormatter(CustomFormatter(
        '%(log_color)s[%(simplename)s] %(message)s',
        log_colors=log_colors))

    logger = logging.getLogger("ddb")
    logger.handlers.clear()
    logger.setLevel(level)
    logger.addHandler(handler)


def handle_watch(watch_started_event=threading.Event(), watch_stop_event=threading.Event()):
    """
    Handle watch option
    """
    watch_supports = []  # type:List[Union[Action, WatchSupport]]
    for action in actions.all():
        if isinstance(action, WatchSupport):
            watch_supports.append(action)

    if watch_supports:
        for watch_support in watch_supports:
            logging.getLogger("ddb.watch").info("Initializing %s watcher ...", watch_support.name)
            watch_support.start_watching()
        watch_started_event.set()
        try:
            logging.getLogger("ddb.watch").warning("Watching ... (CTRL+C to terminate)")
            while not watch_stop_event.wait(1):
                pass
        except KeyboardInterrupt:
            pass
        logging.getLogger("ddb.watch").warning("Terminating ...")
        for action in actions.all():
            if isinstance(action, WatchSupport):
                action.stop_watching()

        for action in actions.all():
            if isinstance(action, WatchSupport):
                action.join_watching()
    else:
        logging.getLogger("ddb.watch").warning("Watching is supported by none enabled features")


class ParseCommandLineException(Exception):
    """
    Exception raised when an invalid command line is given.
    """

    def __init__(self, opts: ArgumentParser, parsed_args: Namespace, unknown_args: List[str]):
        super().__init__()
        self.opts = opts
        self.parsed_args = parsed_args
        self.unknown_args = unknown_args


def parse_command_line(args: Optional[Sequence[str]] = None):
    """
    Parse command line arguments, returning the command to execute, args and unknown args.
    """
    opts = ArgumentParser()
    opts.add_argument('-v', '--verbose', action="store_true",
                      default=config.data.get('defaults.verbose', False),
                      help="Enable more logs")
    opts.add_argument('-vv', '--very-verbose', action="store_true",
                      default=config.data.get('defaults.very_verbose', False),
                      help="Enable even more logs")
    opts.add_argument('-s', '--silent', action="store_true",
                      default=config.data.get('defaults.silent', False),
                      help="Disable all logs")
    opts.add_argument('-x', '--exceptions', action="store_true",
                      default=config.data.get('defaults.exceptions', False),
                      help="Display exceptions on errors")
    opts.add_argument("-c", "--clear-cache", action="store_true",
                      default=config.data.get('defaults.clear_cache', False),
                      help="Clear all caches")
    opts.add_argument('-w', '--watch', action="store_true",
                      default=config.data.get('defaults.watch', False),
                      help="Enable watch mode (hot reload of generated files)")
    opts.add_argument('-ff', '--fail-fast', action="store_true",
                      default=config.data.get('defaults.fail_fast', False),
                      help="Stop on first error")
    opts.add_argument('--version', action="store_true", help='Display the ddb version and check for new ones.')

    command_parsers = {}

    subparsers = opts.add_subparsers(dest="command", help='Available commands')
    for command in commands.all():
        parser = subparsers.add_parser(command.name, help=command.description)
        command.configure_parser(parser)
        command_parsers[command.name] = parser

    parsed_args, unknown_args = opts.parse_known_args(args)

    log_level = 'INFO'
    if parsed_args.very_verbose:
        log_level = 'DEBUG'
    elif parsed_args.verbose:
        log_level = 'VERBOSE'
    elif parsed_args.silent:
        log_level = 'CRITICAL'

    configure_logging(log_level)

    clear_cache = parsed_args.clear_cache
    if clear_cache:
        for cache in caches.all():
            cache.clear()
        logging.getLogger("ddb.cache").success("Cache cleared")

    if not parsed_args.command:
        raise ParseCommandLineException(opts, parsed_args, unknown_args)

    command = commands.get(parsed_args.command)

    if unknown_args and not command.allow_unknown_args:
        msg = _('unrecognized arguments: %s')
        opts.error(msg % ' '.join(unknown_args))

    return command, parsed_args, unknown_args


def handle_command_line(command: Command,
                        watch_started_event=threading.Event(),
                        watch_stop_event=threading.Event()):
    """
    Execute the command and handle additional given arguments like watch mode
    """
    execute_command(command)

    if config.args.watch:
        handle_watch(watch_started_event, watch_stop_event)


def _register_action_in_event_bus(action: Action, binding: Union[Callable, str, EventBinding], fail_fast=False):
    """
    Register a single event binding. It supports name property added by @event decorator on events callable.
    """
    if callable(binding) and hasattr(binding, "name"):
        binding = binding.name
    if isinstance(binding, str):
        binding = EventBinding(binding)
    if callable(binding.event) and hasattr(binding.event, "name"):
        binding.event = binding.event.name

    bus.on(binding.event, action_event_binding_runner_factory(action,
                                                              binding.event,
                                                              to_call=binding.call,
                                                              event_processor=binding.processor,
                                                              fail_fast=fail_fast).run)


def register_actions_in_event_bus(fail_fast=False):
    """
    Register actions into event bus.
    """
    sorted_actions = sorted(actions.all(), key=lambda x: x.order)

    for action in sorted_actions:
        if isinstance(action.event_bindings, (str, EventBinding)) or callable(action.event_bindings):
            _register_action_in_event_bus(action, action.event_bindings, fail_fast)
        else:
            for event_binding in action.event_bindings:
                _register_action_in_event_bus(action, event_binding, fail_fast)


def main(args: Optional[Sequence[str]] = None,
         watch_started_event=threading.Event(),
         watch_stop_event=threading.Event(),
         reset_disabled=False):
    """
    Load all features and handle command line
    """
    try:
        config.load()
        load_plugins()

        register_features()
        load_registered_features()

        try:
            command, args, unknown_args = parse_command_line(args)
            config.args = args
            config.unknown_args = unknown_args
        except ParseCommandLineException as exc:
            config.args = exc.parsed_args
            config.unknown_args = exc.unknown_args
            if not config.args.version:
                exc.opts.print_help()
                raise

        if config.args.version:
            if config.args.silent:
                print(__version__)
            else:
                version_title = 'ddb ' + __version__
                version_content = [
                    [
                        'Please report any bug or feature request at',
                        'https://github.com/gfi-centre-ouest/docker-devbox-ddb/issues'
                    ]
                ]

                last_release = get_lastest_release_version()
                if last_release and __version__ < last_release:
                    version_content.append([
                        '',
                        'A new version is available : ' + last_release,
                        'https://github.com/' + ddb_repository + '/releases/tag/' + last_release,
                        'https://github.com/' + ddb_repository + '/blob/' + last_release + '/CHANGELOG.md',
                        ''
                    ])

                print(get_table_display(version_title, version_content))
            return []

        prepare_project_home()
        register_default_caches()
        register_actions_in_event_bus(config.args.fail_fast)

        handle_command_line(command, watch_started_event, watch_stop_event)
        if command.name not in ['activate', 'deactivate', 'run']:
            _check_for_update()
        return context.exceptions
    finally:
        if not reset_disabled:
            reset()


def _check_for_update():
    register_global_cache('core.version')
    cache = caches.get('core.version')
    last_check = cache.get('last_check', None)
    today = date.today()

    if last_check is None or last_check < today:
        last_release = get_lastest_release_version()
        if last_release and __version__ < last_release:
            header = 'A new version is available : {}'.format(last_release)
            content = [[
                'For more information, check the following links :',
                'https://github.com/{}/releases/tag/{}'.format(ddb_repository, last_release),
                'https://github.com/{}/releases/tag/{}/CHANGELOG.md'.format(ddb_repository, last_release),
            ]]
            print(get_table_display(header, content))

    cache.set('last_check', today)


def clear_caches():
    """
    Clear all caches
    """
    for cache in caches.all():
        cache.clear()
        cache.flush()


def reset():
    """
    Reset all caches and registries to run main method again
    """
    bus.clear()

    features.close()
    phases.close()
    commands.close()
    actions.close()
    binaries.close()
    services.close()
    caches.close()

    context.reset()
    config.reset()

    global _available_features  # pylint:disable=global-statement
    _available_features = list(_default_available_features)


def console_script():  # pragma: no cover
    """
    Console script entrypoint
    """
    try:
        exceptions = main()
    except ParseCommandLineException:
        sys.exit(1)
    if exceptions:
        sys.exit(1)


if __name__ == '__main__':  # pragma: no cover
    console_script()
