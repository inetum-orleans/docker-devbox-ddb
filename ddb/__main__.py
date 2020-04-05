#!/usr/bin/env python
# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from typing import Optional, Sequence, Iterable, Callable

import pkg_resources
from slugify import slugify
from toposort import toposort_flatten

from ddb.command.command import execute_command
from ddb.context import context
from ddb.context.context import configure_context_logger
from .action import actions
from .action.runnerfactory import action_event_binding_runner_factory
from .binary import binaries
from .cache import caches, _project_cache_name, ShelveCache, _global_cache_name, _requests_cache_name
from .command import commands
from .config import config
from .event import bus
from .feature import features, Feature
from .phase import phases
from .registry import Registry, RegistryObject
from .service import services


def register_entrypoint_features():
    """
    Register setuptools entrypoint 'ddb_features' inside features registry.
    Features are registered in order for their dependency to be registered first with a topological sort.
    Withing a command phase, actions are executed in the order of their feature registration.
    """
    entrypoint_features = {}
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
        features.register(entrypoint_features[feature_name])


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
    caches.register(ShelveCache(slugify(config.paths.project_home, regex_pattern=r'[^-a-z0-9_\.]+')),
                    _project_cache_name)
    caches.register(ShelveCache("__global__"), _global_cache_name)
    caches.register(ShelveCache(_requests_cache_name), _requests_cache_name)


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


def handle_command_line(args: Optional[Sequence[str]] = None):
    """
    Handle command line arguments.
    """
    opts = ArgumentParser()
    subparsers = opts.add_subparsers(dest="command", help='Available commands')

    command_parsers = {}

    for command in commands.all():
        parser = subparsers.add_parser(command.name, help=command.description)
        command.configure_parser(parser)
        command_parsers[command.name] = parser

    parsed_args = opts.parse_args(args)

    if parsed_args.command:
        command = commands.get(parsed_args.command)
        kwargs = vars(parsed_args)
        del kwargs['command']
        execute_command(command, **kwargs)
    else:
        opts.print_help()


def register_actions_in_event_bus():
    """
    Register registered actions into event bus.
    """
    sorted_actions = sorted(actions.all(), key=lambda x: x.order)

    for action in sorted_actions:
        if isinstance(action.event_bindings, str):
            event_name = action.event_bindings
            bus.on(event_name, action_event_binding_runner_factory(action, event_name).run)
        else:
            for event_binding in action.event_bindings:
                if isinstance(event_binding, str):
                    event_name = event_binding
                    bus.on(event_name, action_event_binding_runner_factory(action, event_name).run)
                else:
                    event_name, method_name = event_binding
                    bus.on(event_name, action_event_binding_runner_factory(action, event_name, method_name).run)


def main(args: Optional[Sequence[str]] = None):
    """
    Load all features and handle command line
    """
    config.load()
    configure_context_logger()
    register_entrypoint_features()
    register_default_caches()
    load_registered_features()
    register_actions_in_event_bus()
    handle_command_line(args)


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


if __name__ == '__main__':  # pragma: no cover
    main()
