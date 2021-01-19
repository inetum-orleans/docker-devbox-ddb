#!/usr/bin/env python
# -*- coding: utf-8 -*-
import inspect
import logging
import os
import sys
import threading
from argparse import ArgumentParser, Namespace
from gettext import gettext as _
from importlib import import_module
from typing import Optional, Sequence, Iterable, Callable, Union, List

import verboselogs
from colorlog import default_log_colors, ColoredFormatter

from ddb.action import actions
from ddb.action.action import EventBinding, Action, WatchSupport
from ddb.action.runner import ExpectedError
from ddb.action.runnerfactory import action_event_binding_runner_factory
from ddb.binary import binaries
from ddb.cache import caches, global_cache_name, requests_cache_name, \
    project_binary_cache_name, register_global_cache, project_cache_name
from ddb.cache import register_project_cache
from ddb.command import commands
from ddb.command.command import execute_command, Command
from ddb.config import config
from ddb.context import context
from ddb.event import bus, events
from ddb.feature import features, Feature
from ddb.feature.bootstrap import reset_available_features, append_available_feature, \
    load_bootstrap_config, bootstrap_register_features
from ddb.feature.core import ConfigureSecondPassException
from ddb.phase import phases
from ddb.registry import Registry, RegistryObject
from ddb.service import services

_watch_started_event = threading.Event()
_watch_stop_event = threading.Event()


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
            append_available_feature(feature)


def prepare_project_home():
    """
    Set working directory to project home.
    """
    if config.paths.project_home:
        config.cwd = os.getcwd()
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


def preload_registered_features():
    """
    Load phases and commands from all registered features.
    """
    load_bootstrap_config()
    all_features = features.all()
    enabled_features = [f for f in all_features if not f.disabled]  # type: Iterable[Feature]
    register_objects(enabled_features, lambda f: f.phases, phases)
    register_objects(enabled_features, lambda f: f.commands, commands)
    return enabled_features


def load_registered_features(preload=True):
    """
    Load all registered features.
    """
    if preload:
        load_bootstrap_config()

    all_features = features.all()

    for feature in all_features:
        feature.before_load()

    try:
        for feature in all_features:
            feature.configure()
    except ConfigureSecondPassException:
        config.clear()
        load_bootstrap_config()

        for feature in all_features:
            feature.configure()

    # migrations.compat(config.data)

    enabled_features = [f for f in all_features if not f.disabled]  # type: Iterable[Feature]

    if preload:
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
        _watch_started_event.set()
        try:
            context.watching = True
            logging.getLogger("ddb.watch").warning("Watching ... (CTRL+C to terminate)")
            while not _watch_stop_event.wait(1):
                pass
        except KeyboardInterrupt:
            pass
        finally:
            context.watching = False
        logging.getLogger("ddb.watch").warning("Terminating ...")
        for watch_support in watch_supports:
            watch_support.stop_watching()

        for watch_support in watch_supports:
            watch_support.join_watching()
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
                      help="Clear all used caches")
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
        parser = command.add_parser(subparsers)
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

    if not parsed_args.command:
        raise ParseCommandLineException(opts, parsed_args, unknown_args)

    command = commands.get(parsed_args.command)

    if unknown_args and not command.allow_unknown_args:
        msg = _('unrecognized arguments: %s')
        opts.error(msg % ' '.join(unknown_args))

    return command, parsed_args, unknown_args


def handle_command_line(command: Command):
    """
    Execute the command and handle additional given arguments like watch mode
    """
    execute_command(command)

    if config.args.watch:
        handle_watch()


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


def main(args: Optional[Sequence[str]] = None,  # pylint:disable=too-many-statements
         reset_disabled=False,
         before_handle_command_line=None):
    """
    Load all features and handle command line
    """
    global _watch_started_event, _watch_stop_event  # pylint:disable=global-statement
    _watch_started_event = threading.Event()
    _watch_stop_event = threading.Event()
    initial_cwd = os.getcwd()
    try:
        load_plugins()
        bootstrap_register_features()
        preload_registered_features()

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

        load_registered_features(False)
        register_actions_in_event_bus(config.args.fail_fast)

        if config.args.version:
            events.main.version(silent=config.args.silent)
            return []

        prepare_project_home()
        register_default_caches()

        def on_config_reloaded():
            global _watch_started_event, _watch_stop_event  # pylint:disable=global-statement
            _watch_stop_event.set()
            _watch_started_event = threading.Event()
            _watch_stop_event = threading.Event()

            for action in actions.all():
                if hasattr(action, "destroy") and callable(action.destroy):
                    action.destroy()
                if hasattr(action, "initialized") and action.initialized:
                    action.initialized = False

            context.reset()

            handle_command_line(command)

        bus.on(events.config.reloaded.name, on_config_reloaded)  # pylint:disable=no-member

        events.main.start(command=command)
        handle_command_line(command)

        events.main.terminate(command=command)

        return context.exceptions
    except ExpectedError as exception:
        return [exception]
    except Exception as exception:  # pylint:disable=broad-except
        try:
            clear_caches()
        except Exception as clear_cache_exception:  # pylint:disable=broad-except
            logging.getLogger('ddb').exception("An error has occured while clearing caches",
                                               exc_info=clear_cache_exception)
        raise exception
    finally:
        os.chdir(initial_cwd)
        if not reset_disabled:
            reset()


def wait_watch_started(timeout: Optional[float] = None):
    """
    Wait for watch mode to be started.
    """
    return _watch_started_event.wait(timeout)


def stop_watch():
    """
    Stop watch mode.
    """
    _watch_stop_event.set()


def clear_caches():
    """
    Clear all caches
    """
    for cache in caches.all():
        cache.clear()
        cache.flush()


def reset():
    """
    Close all caches and reset registries to run main method again
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

    reset_available_features()


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
