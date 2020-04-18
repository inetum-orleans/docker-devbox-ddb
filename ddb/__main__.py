#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import sys
import time
from argparse import ArgumentParser
from gettext import gettext as _
from typing import Optional, Sequence, Iterable, Callable, Union, List

import pkg_resources
import verboselogs
from colorlog import default_log_colors, ColoredFormatter
from slugify import slugify
from toposort import toposort_flatten

from ddb.action import actions
from ddb.action.action import EventBinding, Action, WatchSupport
from ddb.action.runnerfactory import action_event_binding_runner_factory
from ddb.binary import binaries
from ddb.cache import caches, _project_cache_name, ShelveCache, _global_cache_name, _requests_cache_name, \
    _project_binary_cache_name
from ddb.command import commands
from ddb.command.command import execute_command
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
from ddb.feature.gitignore import GitignoreFeature
from ddb.feature.jinja import JinjaFeature
from ddb.feature.jsonnet import JsonnetFeature
from ddb.feature.plugins import PluginsFeature
from ddb.feature.run import RunFeature
from ddb.feature.shell import ShellFeature
from ddb.feature.symlinks import SymlinksFeature
from ddb.feature.traefik import TraefikFeature
from ddb.feature.ytt import YttFeature
from ddb.phase import phases
from ddb.registry import Registry, RegistryObject
from ddb.service import services


def get_default_features():
    """
    Default features. Setuptools entrypoint are bypassed for those features to enhance bootstrap performance.
    """
    return (
        CertsFeature(),
        CopyFeature(),
        CoreFeature(),
        DockerFeature(),
        FileFeature(),
        FixuidFeature(),
        GitignoreFeature(),
        JinjaFeature(),
        JsonnetFeature(),
        PluginsFeature(),
        RunFeature(),
        ShellFeature(),
        SymlinksFeature(),
        TraefikFeature(),
        YttFeature()
    )


def register_features(default_features: Iterable[Feature] = get_default_features()):
    """
    Register default features and setuptools entrypoint 'ddb_features' inside features registry.
    Features are registered in order for their dependency to be registered first with a topological sort.
    Withing a command phase, actions are executed in the order of their feature registration.
    """
    entrypoint_features = {f.name: f for f in default_features}
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


def register_default_caches():
    """
    Register default caches.
    """
    caches.register(
        ShelveCache(slugify(_project_cache_name + '.' + config.paths.project_home,
                            regex_pattern=r'[^-a-z0-9_\.]+')),
        _project_cache_name)
    caches.register(ShelveCache(_global_cache_name), _global_cache_name)
    caches.register(ShelveCache(_requests_cache_name), _requests_cache_name)
    caches.register(
        ShelveCache(
            slugify(_project_binary_cache_name + '.' + config.paths.project_home,
                    regex_pattern=r'[^-a-z0-9_\.]+')), _project_binary_cache_name)
    binaries.set_cache(caches.get(_project_binary_cache_name))


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
    logger.setLevel(level)
    logger.addHandler(handler)


def handle_watch():
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

        try:
            logging.getLogger("ddb.watch").warning("Watching ... (CTRL+C to terminate)")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logging.getLogger("ddb.watch").warning("Terminating ...")
            for action in actions.all():
                if isinstance(action, WatchSupport):
                    action.stop_watching()

        for action in actions.all():
            if isinstance(action, WatchSupport):
                action.join_watching()
    else:
        logging.getLogger("ddb.watch").warning("Watching is supported by none enabled features")


def handle_command_line(args: Optional[Sequence[str]] = None):
    """
    Handle command line arguments.
    """
    opts = ArgumentParser()
    subparsers = opts.add_subparsers(dest="command", help='Available commands')

    opts.add_argument('-v', '--verbose', action="store_true", default=False,
                      help="Enable more logs")
    opts.add_argument('-vv', '--very-verbose', action="store_true", default=False,
                      help="Enable even more logs")
    opts.add_argument('-s', '--silent', action="store_true", default=False,
                      help="Disable all logs")
    opts.add_argument("-c", "--clear-cache", action="store_true", default=None,
                      help="Clear all caches")
    opts.add_argument('-w', '--watch', action="store_true", default=False,
                      help="Enable watch mode (hot reload of generated files")

    command_parsers = {}

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

    if parsed_args.command:
        command = commands.get(parsed_args.command)

        if unknown_args and not command.allow_unknown_args:
            msg = _('unrecognized arguments: %s')
            opts.error(msg % ' '.join(unknown_args))

        config.args = parsed_args
        config.unknown_args = unknown_args
        execute_command(command)

        if parsed_args.watch:
            handle_watch()
    else:
        opts.print_help()


def _register_action_in_event_bus(action: Action, binding: Union[str, EventBinding], fail_fast=False):
    """
    Register a single event binding
    """
    if isinstance(binding, str):
        binding = EventBinding(binding)

    bus.on(binding.event, action_event_binding_runner_factory(action,
                                                              binding.event,
                                                              to_call=binding.call,
                                                              event_processor=binding.processor,
                                                              fail_fast=fail_fast).run)


def register_actions_in_event_bus(fail_fast=False):
    """
    Register registered actions into event bus.
    """
    sorted_actions = sorted(actions.all(), key=lambda x: x.order)

    for action in sorted_actions:
        if isinstance(action.event_bindings, (str, EventBinding)):
            _register_action_in_event_bus(action, action.event_bindings, fail_fast)
        else:
            for event_binding in action.event_bindings:
                _register_action_in_event_bus(action, event_binding, fail_fast)


def main(args: Optional[Sequence[str]] = None):
    """
    Load all features and handle command line
    """
    config.load()
    register_default_caches()
    register_features()
    load_registered_features()
    register_actions_in_event_bus()
    handle_command_line(args)
    return context.exceptions


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
    clear_caches()

    caches.clear()
    bus.clear()
    features.clear()
    phases.clear()
    commands.clear()
    actions.clear()
    binaries.clear()
    services.clear()

    context.reset()
    config.reset()


def console_script():  # pragma: no cover
    """
    Console script entrypoint
    """
    exceptions = main()
    if exceptions:
        sys.exit(1)


if __name__ == '__main__':  # pragma: no cover
    console_script()
