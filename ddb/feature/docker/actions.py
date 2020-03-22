# -*- coding: utf-8 -*-
import os
from subprocess import run, PIPE
from typing import Iterable

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
    Emit docker:docker-compose-config event with docker compose configuration
    """

    @property
    def event_name(self) -> str:
        return "phase:post-configure"

    @property
    def name(self) -> str:
        return "docker:emit-docker-compose-config"

    @property
    def disabled(self) -> bool:
        return bus.has_named_listeners("docker:docker-compose-config")

    def execute(self, *args, **kwargs):
        # TODO: Add support for custom docker-compose -f option (custom filename and multiple files)
        if os.path.exists("docker-compose.yml"):
            yaml_output = run_docker_compose("config")
            parsed_config = yaml.load(yaml_output, yaml.SafeLoader)
            docker_compose_config = Dotty(parsed_config)

            bus.emit("docker:docker-compose-config", config=docker_compose_config)
