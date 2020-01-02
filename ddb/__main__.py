#!/usr/bin/env python
# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from typing import Optional, Sequence, Iterable, Callable, Any

from slugify import slugify

from ddb.feature.symlinks import SymlinksFeature
from .action import actions
from .binary import binaries
from .cache import caches, _project_cache_name, ShelveCache, _global_cache_name
from .command import commands
from .config import config
from .event import bus
from .feature import features, Feature
from .feature.core import CoreFeature
from .feature.docker import DockerFeature
from .feature.plugins import PluginsFeature
from .feature.shell import ShellFeature
from .phase import phases
from .registry import Registry
from .service import services


def register_default_features():
    """
    Register default features inside features registry.
    """
    features.register(CoreFeature())
    features.register(ShellFeature())
    features.register(DockerFeature())
    features.register(PluginsFeature())
    features.register(SymlinksFeature())


def register_default_caches():
    """
    Register default caches.
    """
    caches.register(ShelveCache(slugify(config.paths.project_home, regex_pattern=r'[^-a-z0-9_\.]+')),
                    _project_cache_name)
    caches.register(ShelveCache("__global__"), _global_cache_name)


def register_objects(features_list: Iterable[Feature],
                     objects_getter: Callable[[Feature], Any],
                     registry: Registry[Any]):
    """
    Register objects from features inside registry.
    """
    for feature in features_list:
        for obj in objects_getter(feature):
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

    enabled_features = [f for f in all_features if not f.disabled]

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
        command.execute(**vars(parsed_args))
    else:
        opts.print_help()


def register_actions_in_event_bus():
    """
    Register registered actions into event bus.
    """
    for action in actions.all():
        bus.on(action.event_name, action.run)


def main(args: Optional[Sequence[str]] = None):
    """
    Load all features and handle command line
    """
    register_default_features()
    register_default_caches()
    load_registered_features()
    register_actions_in_event_bus()
    handle_command_line(args)


def reset():
    """
    Reset all caches and registries to run main method again
    """

    for cache in caches.all():
        cache.close()

    caches.clear()
    bus.clear()
    features.clear()
    phases.clear()
    commands.clear()
    actions.clear()
    binaries.clear()
    services.clear()

    config.reset()


if __name__ == '__main__':  # pragma: no cover
    main()
