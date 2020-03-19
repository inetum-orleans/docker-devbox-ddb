# -*- coding: utf-8 -*-
import json
import os
import re
import shlex
from collections import namedtuple
from subprocess import run, PIPE

import docker
import yaml
from cached_property import cached_property
from dockerfile_parse import DockerfileParser
from dotty_dict import Dotty

from ..copy.actions import copy_from_url
from ...action import Action
from ...cache import global_cache
from ...config import config

BuildServiceDef = namedtuple("BuildServiceDef", "context dockerfile")


class CustomDockerfileParser(DockerfileParser):
    """
    Custom class to implement entrypoint property with the same behavior as cmd property.
    """

    def get_last_instruction(self, instruction_type):
        """
        Determine the final instruction_type instruction, if any, in the final build stage.
        instruction_types from earlier stages are ignored.
        :return: value of final stage instruction_type instruction
        """
        last_instruction = None
        for insndesc in self.structure:
            if insndesc['instruction'] == 'FROM':  # new stage, reset
                last_instruction = None
            elif insndesc['instruction'] == instruction_type:
                last_instruction = insndesc
        return last_instruction

    @property
    def entrypoint(self):
        """
        Determine the final ENTRYPOINT instruction, if any, in the final build stage.
        ENTRYPOINTs from earlier stages are ignored.
        :return: value of final stage ENTRYPOINT instruction
        """
        last_instruction = self.get_last_instruction("ENTRYPOINT")
        return last_instruction['value'] if last_instruction else None

    @entrypoint.setter
    def entrypoint(self, value):
        """
        setter for final 'ENTRYPOINT' instruction in final build stage

        """
        entrypoint = None
        for insndesc in self.structure:
            if insndesc['instruction'] == 'FROM':  # new stage, reset
                entrypoint = None
            elif insndesc['instruction'] == 'ENTRYPOINT':
                entrypoint = insndesc

        new_entrypoint = 'ENTRYPOINT ' + value
        if entrypoint:
            self.add_lines_at(entrypoint, new_entrypoint, replace=True)
        else:
            self.add_lines(new_entrypoint)


class FixuidAction(Action):
    """
    Automate fixuid configuration for services where fixuid.yml configuration file is available in context
    """

    @property
    def event_name(self) -> str:
        return "phase:post-configure"

    @property
    def name(self) -> str:
        return "docker:fixuid"

    @property
    def disabled(self) -> bool:
        return not config.data.get("docker.fixuid")

    @cached_property
    def docker_compose_config(self) -> Dotty:  # pylint:disable=no-self-use
        """

        :return:
        """
        docker_compose_bin = config.data["docker.compose.bin"]
        docker_compose_args = config.data.get("docker.compose.args", [])

        process = run([docker_compose_bin] + docker_compose_args + ["config"],
                      check=True,
                      stdout=PIPE, stderr=PIPE)

        yaml_output = process.stdout
        if os.name == "nt":
            # On windows, there's ANSI code after the yaml output that has to be dropped...
            try:
                eof_index = yaml_output.index(b"\x1b[0m")
                yaml_output = yaml_output[:eof_index]
            except ValueError:
                pass

        parsed_config = yaml.load(yaml_output, yaml.SafeLoader)
        return Dotty(parsed_config)

    @staticmethod
    def _load_image_attrs(image):
        client = docker.from_env()
        registry_data = client.images.get_registry_data(image)

        cache_key = "docker.image." + registry_data.id + ".attrs"
        image_attrs = global_cache().get(cache_key)

        if not image_attrs:
            image = registry_data.pull()
            image_attrs = image.attrs
            global_cache().set(cache_key, image_attrs)
        return image_attrs

    @staticmethod
    def _get_image_config(image):
        if image and image != 'scratch':
            attrs = FixuidAction._load_image_attrs(image)
            if attrs and 'Config' in attrs:
                return attrs['Config']
        return None

    @staticmethod
    def _apply_fixuid(service: BuildServiceDef):
        dockerfile_path = os.path.join(service.context, service.dockerfile)

        with open(dockerfile_path, "r") as dockerfile_file:
            dockerfile = dockerfile_file.read()

        parser = CustomDockerfileParser()
        parser.content = dockerfile

        entrypoint = parser.entrypoint
        cmd = parser.cmd

        # if entrypoint is defined in Dockerfile, we should not grab cmd from base image and reset CMD to empty value
        # to stay consistent with docker behavior.
        # see https://github.com/docker/docker.github.io/issues/6142
        reset_cmd = False
        if entrypoint and not cmd:
            reset_cmd = True

        if not entrypoint:
            baseimage_config = FixuidAction._get_image_config(parser.baseimage)
            if baseimage_config and 'Entrypoint' in baseimage_config:
                entrypoint = baseimage_config['Entrypoint']
                entrypoint = json.dumps(entrypoint)

        if not cmd and not reset_cmd:
            baseimage_config = FixuidAction._get_image_config(parser.baseimage)
            if baseimage_config and 'Cmd' in baseimage_config:
                cmd = baseimage_config['Cmd']
                cmd = json.dumps(cmd)

        if not cmd:
            cmd = None

        if entrypoint:
            parser.entrypoint = FixuidAction._sanitize_entrypoint(entrypoint)

        if cmd:
            parser.cmd = cmd

        copy_from_url("https://github.com/boxboat/fixuid/releases/download/v0.4/fixuid-0.4-linux-amd64.tar.gz",
                      service.context,
                      "fixuid.tar.gz")

        lines = ("ADD fixuid.tar.gz /usr/local/bin",
                 "RUN chown root:root /usr/local/bin/fixuid && "
                 "chmod 4755 /usr/local/bin/fixuid && "
                 "mkdir -p /etc/fixuid",
                 "COPY fixuid.yml /etc/fixuid/config.yml")

        last_instruction_user = parser.get_last_instruction("USER")
        last_instruction_entrypoint = parser.get_last_instruction("ENTRYPOINT")
        if last_instruction_user:
            parser.add_lines_at(last_instruction_user, *lines)
        elif last_instruction_entrypoint:
            parser.add_lines_at(last_instruction_entrypoint, *lines)
        else:
            parser.add_lines(*lines)

        with open(dockerfile_path, "w", encoding="utf-8") as dockerfile_file:
            dockerfile_file.write(parser.content)

    def execute(self, *args, **kwargs):
        services = []

        if not os.path.exists("docker-compose.yml"):
            return

        if "services" not in self.docker_compose_config:
            return

        for _, service in self.docker_compose_config.get("services").items():
            if "build" not in service.keys():
                continue

            if isinstance(service["build"], dict):
                context = Dotty(service).get("build.context")
            elif isinstance(service["build"], str):
                context = service["build"]
            else:
                continue

            if not os.path.exists(os.path.join(context, "fixuid.yml")):
                continue

            dockerfile = Dotty(service).get("build.dockerfile", "Dockerfile")
            services.append(BuildServiceDef(context, dockerfile))

        for service in services:
            self._apply_fixuid(service)

    @staticmethod
    def _sanitize_entrypoint(entrypoint):
        as_list = False
        start_quote = ""
        end_quote = ""

        if entrypoint.startswith("["):
            as_list = True
            entrypoint_list = json.loads(entrypoint)
        else:
            entrypoint_match = re.compile(r"^(['\"]?)(.*?)(['\"]?)$").match(entrypoint)
            start_quote = entrypoint_match.group(1)
            end_quote = entrypoint_match.group(3)
            entrypoint = entrypoint_match.group(2)
            entrypoint_list = shlex.split(entrypoint)

        entrypoint_list = ["fixuid", "-q"] + entrypoint_list
        if as_list:
            entrypoint = json.dumps(entrypoint_list)
        else:
            entrypoint = " ".join(entrypoint_list)
            entrypoint = "%s%s%s" % (start_quote, entrypoint, end_quote)

        return entrypoint
