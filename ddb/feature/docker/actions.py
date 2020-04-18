# -*- coding: utf-8 -*-
import os
import re
from subprocess import run, PIPE, CalledProcessError
from typing import Iterable

import simpleeval
import yaml
from dotty_dict import Dotty

from .binaries import DockerBinary
from ...action import Action
from ...action.action import EventBinding
from ...binary import binaries
from ...config import config
from ...context import context
from ...event import bus


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
        self._executed = False
        self.key_re = re.compile(r"^\s*ddb\.emit\.(.+?)(?:\[(.+?)\])?(?:\((.+?)\))?\s*$")
        self.eval_re = re.compile(r"^\s*eval\((.*)\)\s*$")

    @property
    def event_bindings(self):
        return (
            "phase:configure",
            EventBinding("file:generated",
                         processor=lambda source, target: ((), {}) if target == "docker-compose.yml" else False)
        )

    @property
    def name(self) -> str:
        return "docker:emit-docker-compose-config"

    def execute(self):
        """
        Execute action
        """

        if self._executed:
            return

        # TODO: Add support for custom docker-compose -f option (custom filename and multiple files)
        if not os.path.exists("docker-compose.yml"):
            return

        try:
            yaml_output = run_docker_compose("config")
        except CalledProcessError as exc:
            context.log.error(str(exc))
            context.log.error(exc.stderr)
            return

        parsed_config = yaml.load(yaml_output, yaml.SafeLoader)
        docker_compose_config = Dotty(parsed_config)

        self._executed = True

        bus.emit("docker:docker-compose-config", docker_compose_config=docker_compose_config)

        services = docker_compose_config.get('services')
        if not services:
            return

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
                val = simpleeval.simple_eval(eval_match.group(1), names=names)

            if var:
                kwargs[var] = val
            else:
                args.append(val)

        return args, kwargs


class DockerComposeBinaryAction(Action):
    """
    Convert ddb.event.bus.emit.docker:binary events to binary available from shell.
    """

    @property
    def event_bindings(self):
        return "docker:binary"

    @property
    def name(self) -> str:
        return "docker:docker-compose-binary"

    @staticmethod
    def execute(name=None, workdir=None, options=None, args=None, docker_compose_service=None):
        """
        Execute action
        """
        if name is None and docker_compose_service:
            name = docker_compose_service
        if name is None:
            raise ValueError("name should be defined")

        binary = DockerBinary(name, docker_compose_service, workdir, options, args)

        if binaries.has(name):
            existing_binary = binaries.get(name)
            if existing_binary.command() == binary.command():
                context.log.notice("Binary registered: %s" % (name,))
                return

            binaries.unregister(name)

        binaries.register(binary)

        context.log.success("Binary registered: %s", name)
        bus.emit("binary:registered", binary=binary)
