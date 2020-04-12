# -*- coding: utf-8 -*-
import os
import re
from subprocess import run, PIPE
from typing import Iterable, Union, Callable

import simpleeval
import yaml
from dotty_dict import Dotty

from ...action import Action
from ...config import config
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
        self.key_re = re.compile(r"^\s*ddb\.event\.bus\.emit\.(.+?)(?:\[.*\])?\s*$")
        self.eval_re = re.compile(r"^\s*eval\((.*)\)\s*$")

    @property
    def event_bindings(self) -> Union[str, Iterable[Union[Iterable[str], Callable]]]:
        return "phase:post-configure"

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

        bus.emit("docker:docker-compose-config", docker_compose_config=docker_compose_config)

        services = docker_compose_config.get('services')
        if not services:
            return

        for service in services.values():
            labels = service.get('labels')
            if not labels:
                continue

            if not isinstance(labels, dict):
                labels = {label.split("=", 1) for label in labels}

            for key, value in labels.items():
                match = self.key_re.match(key)
                if not match:
                    continue

                event_name = match.group(1)
                names = {"service": service, "config": docker_compose_config}
                self.emit_event(event_name, value, names)

    def emit_event(self, event_name, value, names=None):
        """
        Emit an event from raw value.
        """
        values = map(str.strip, value.split("|"))

        args = []
        kwargs = {}

        for expression in values:
            if "=" in expression:
                var, val = expression.split("=", 1)
            else:
                var, val = None, expression

            eval_match = self.eval_re.match(val)
            if eval_match:
                val = simpleeval.simple_eval(eval_match.group(1), names=names)

            if var:
                kwargs[var] = val
            else:
                args.append(val)

        bus.emit(event_name, *args, **kwargs)
