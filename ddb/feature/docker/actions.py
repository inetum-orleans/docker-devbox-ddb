# -*- coding: utf-8 -*-
import os
import re
from subprocess import run, PIPE
from typing import Iterable

from simpleeval import simple_eval
import yaml
from dotty_dict import Dotty

from .binaries import DockerBinary
from ...action import Action
from ...action.action import EventBinding, InitializableAction
from ...binary import binaries
from ...cache import caches, register_project_cache
from ...config import config
from ...context import context
from ...event import bus, events


def run_docker_compose(*params: Iterable[str]):
    """
    Run docker-compose command.
    """
    docker_compose_bin = config.data["docker.compose.bin"]
    docker_compose_args = config.data.get("docker.compose.args", [])

    process = run([docker_compose_bin] + docker_compose_args + list(params),
                  check=True,
                  stdout=PIPE, stderr=PIPE)

    stdout = process.stdout
    if os.name == "nt":
        # On windows, there's ANSI code after output that has to be dropped...
        try:
            eof_index = stdout.index(b"\x1b[0m")
            stdout = stdout[:eof_index]
        except ValueError:
            pass
    return stdout


class EmitDockerComposeConfigAction(Action):
    """
    Emit docker:docker-compose-config event with docker compose configuration,
    and events from ddb.event.bus.emit.<event-name>=prop1=prop1_value;prop2=int(prop2_value) labels.
    To generate multiple events of same name in the same service, event-name can be suffixed with "[xxx]".
    """

    def __init__(self):
        super().__init__()
        self.current_yaml_output = None
        self.key_re = re.compile(r"^\s*ddb\.emit\.(.+?)(?:\[(.+?)\])?(?:\((.+?)\))?\s*$")
        self.eval_re = re.compile(r"^\s*eval\((.*)\)\s*$")

    @property
    def event_bindings(self):
        return (
            events.phase.configure,
            EventBinding(events.file.generated,
                         processor=lambda source, target: ((), {}) if target == "docker-compose.yml" else False)
        )

    @property
    def name(self) -> str:
        return "docker:emit-docker-compose-config"

    def execute(self):
        """
        Execute action
        """
        # TODO: Add support for custom docker-compose -f option (custom filename and multiple files)
        if not os.path.exists("docker-compose.yml"):
            return

        yaml_output = run_docker_compose("config")

        parsed_config = yaml.load(yaml_output, yaml.SafeLoader)
        docker_compose_config = Dotty(parsed_config)

        if self.current_yaml_output == yaml_output:
            return
        self.current_yaml_output = yaml_output

        events.docker.docker_compose_config(docker_compose_config=docker_compose_config)

        services = docker_compose_config.get('services')
        if not services:
            return

        events.docker.docker_compose_before_events(docker_compose_config=docker_compose_config)

        for service_name, service in services.items():
            labels = service.get('labels')
            if not labels:
                continue

            if not isinstance(labels, dict):
                labels = {label.split("=", 1) for label in labels}

            event_data = self._build_event_data(docker_compose_config, labels, service, service_name)

            for (event_name, event_parsed_values) in event_data.items():
                for _, (args, kwargs) in event_parsed_values.items():
                    bus.emit(event_name, *args, **kwargs)

        events.docker.docker_compose_after_events(docker_compose_config=docker_compose_config)

    def _build_event_data(self, docker_compose_config, labels, service, service_name):  # pylint:disable=too-many-locals
        parsed_values = {}
        for key, value in labels.items():
            match = self.key_re.match(key)
            if not match:
                continue

            event_name = match.group(1)
            event_id = match.group(2)
            property_name = match.group(3)

            args, kwargs = self._parse_value(value,
                                             {"service": service, "config": docker_compose_config},
                                             property_name)
            kwargs["docker_compose_service"] = service_name

            event_parsed_values = parsed_values.get(event_name)
            if not event_parsed_values:
                event_parsed_values = dict()
                parsed_values[event_name] = event_parsed_values

            if event_id in event_parsed_values:
                event_args, event_kwargs = event_parsed_values[event_id]
                event_args.extend(args)
                event_kwargs.update(kwargs)
            else:
                event_parsed_values[event_id] = args, kwargs
        return parsed_values

    def _parse_value(self, value, names, property_name=None):
        values = map(str.strip, value.split("|")) if not property_name else [value]

        args = []
        kwargs = {}

        for expression in values:
            if not property_name and "=" in expression:
                var, val = expression.split("=", 1)
            else:
                var, val = property_name, expression

            eval_match = self.eval_re.match(val)
            if eval_match:
                val = simple_eval(eval_match.group(1), names=names)

            if var:
                kwargs[var] = val
            else:
                args.append(val)

        return args, kwargs


class DockerComposeBinaryAction(InitializableAction):
    """
    Convert ddb.event.bus.emit.docker:binary events to binary available from shell.
    """

    def __init__(self):
        super().__init__()
        self.binaries = dict()

    @property
    def event_bindings(self):
        return (events.docker.binary,
                EventBinding(events.docker.docker_compose_before_events, call=self.before_events),
                EventBinding(events.docker.docker_compose_after_events, call=self.after_events))

    @property
    def name(self) -> str:
        return "docker:docker-compose-binary"

    def initialize(self):
        register_project_cache("docker.binaries")

    def before_events(self, docker_compose_config):
        """
        Reset current binaries dict.
        """
        self.binaries = dict()

    def after_events(self, docker_compose_config):
        """
        Cache binaries and remove binaries from cache that are not found in current config.
        """
        docker_binaries_cache = caches.get("docker.binaries")

        for name, binary in self.binaries.items():
            docker_binaries_cache.set(name, binary)

        binaries_to_remove = set()
        for name in docker_binaries_cache.keys():
            if name not in self.binaries.keys():
                unregistered_binary = binaries.unregister(name)
                events.binary.unregistered(binary=unregistered_binary)
                binaries_to_remove.add(name)

        for binary_to_remove in binaries_to_remove:
            docker_binaries_cache.pop(binary_to_remove)

        docker_binaries_cache.flush()

    def execute(self, name=None, workdir=None, options=None, options_condition=None, args=None,
                docker_compose_service=None):
        """
        Execute action
        """
        if name is None and docker_compose_service:
            name = docker_compose_service
        if name is None:
            raise ValueError("name should be defined")

        binary = DockerBinary(name, docker_compose_service=docker_compose_service, workdir=workdir, options=options,
                              options_condition=options_condition, args=args)

        self.binaries[name] = binary

        if binaries.has(name):
            existing_binary = binaries.get(name)
            if existing_binary.command() == binary.command():
                context.log.notice("Binary exists: %s" % (name,))
                events.binary.found(binary=binary)
                return

            binaries.unregister(name)

        binaries.register(binary)

        context.log.success("Binary registered: %s", name)
        events.binary.registered(binary=binary)
