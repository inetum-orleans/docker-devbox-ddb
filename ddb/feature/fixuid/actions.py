# -*- coding: utf-8 -*-
import json
import os
import re
import shlex
from collections import namedtuple
from typing import Iterable

import docker
from chmod_monkey import tmp_chmod
from dockerfile_parse import DockerfileParser
from dotty_dict import Dotty

from ..copy.actions import copy_from_url
from ...action import Action
from ...action.action import EventBinding
from ...cache import global_cache
from ...config import config
from ...context import context
from ...event import events
from ...utils.file import force_remove

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

        if value:
            new_entrypoint = 'ENTRYPOINT ' + value
        else:
            new_entrypoint = None

        if entrypoint:
            if new_entrypoint:
                self.add_lines_at(entrypoint, new_entrypoint, replace=True)
            else:
                new_lines = list(self.lines)
                new_lines.remove(entrypoint['content'])
                self.lines = new_lines
        elif new_entrypoint:
            self.add_lines(new_entrypoint)

    @property
    def cmd(self):
        """
        Determine the final CMD instruction, if any, in the final build stage.
        CMDs from earlier stages are ignored.
        :return: value of final stage CMD instruction
        """
        value = None
        for insndesc in self.structure:
            if insndesc['instruction'] == 'FROM':  # new stage, reset
                value = None
            elif insndesc['instruction'] == 'CMD':
                value = insndesc['value']
        return value

    @cmd.setter
    def cmd(self, value):
        """
        setter for final 'CMD' instruction in final build stage

        """
        cmd = None
        for insndesc in self.structure:
            if insndesc['instruction'] == 'FROM':  # new stage, reset
                cmd = None
            elif insndesc['instruction'] == 'CMD':
                cmd = insndesc

        if value:
            new_cmd = 'CMD ' + value
        else:
            new_cmd = None
        if cmd:
            if new_cmd:
                self.add_lines_at(cmd, new_cmd, replace=True)
            else:
                new_lines = list(self.lines)
                new_lines.remove(cmd['content'])
                self.lines = new_lines
        elif new_cmd:
            self.add_lines(new_cmd)


class FixuidDockerComposeAction(Action):
    """
    Automate fixuid configuration for docker compose services where fixuid.yml configuration file is available in
    build context
    """

    def __init__(self):
        self.docker_compose_config = dict()
        self._dockerfile_lines = ("ADD fixuid.tar.gz /usr/local/bin",
                                  "RUN chown root:root /usr/local/bin/fixuid && "
                                  "chmod 4755 /usr/local/bin/fixuid && "
                                  "mkdir -p /etc/fixuid",
                                  "COPY fixuid.yml /etc/fixuid/config.yml")

    @property
    def event_bindings(self):
        def file_generated_processor(source: str, target: str):
            service = self.find_fixuid_service(target)
            if service:
                return (), {"service": service}
            return None

        def file_found_processor(file: str):
            if os.path.basename(file) == 'fixuid.yml':
                dockerfile_filepath = os.path.join(os.path.dirname(file), 'Dockerfile')
                service = self.find_fixuid_service(dockerfile_filepath)
                if service:
                    return (), {"service": service}
            return None

        def file_deleted_processor(file: str):
            if os.path.basename(file) == 'fixuid.yml':
                dockerfile_filepath = os.path.join(os.path.dirname(file), 'Dockerfile')
                service = self.find_fixuid_service(dockerfile_filepath, include_missing_fixuid=True)
                if service:
                    return (), {"service": service}
            return None

        return (
            events.docker.docker_compose_config,
            EventBinding(events.file.generated,
                         call=self.apply_fixuid,
                         processor=file_generated_processor),
            EventBinding(events.file.found,
                         call=self.apply_fixuid,
                         processor=file_found_processor),
            EventBinding(events.file.deleted,
                         call=self.remove_fixuid,
                         processor=file_deleted_processor)
        )

    @property
    def name(self) -> str:
        return "fixuid:docker"

    @staticmethod
    def _get_registry_data(image):
        context.log.warning("Loading registry data id for image %s...", image)
        client = docker.from_env()
        registry_data = client.images.get_registry_data(image)
        context.log.success("Id retrieved for image %s (%s)", image, registry_data.id)
        return registry_data

    @staticmethod
    def _load_image_attrs(image):
        registry_data_id_cache_key = "docker.image.name." + image + ".registry_data"
        registry_data_id = global_cache().get(registry_data_id_cache_key)
        registry_data = None
        if not registry_data_id:
            registry_data = FixuidDockerComposeAction._get_registry_data(image)
            registry_data_id = registry_data.id
            global_cache().set(registry_data_id_cache_key, registry_data_id)
        else:
            context.log.notice("Id retrieved for image %s (%s) (from cache)", image, registry_data_id)

        image_attrs_cache_key = "docker.image.id." + registry_data_id + ".attrs"
        image_attrs = global_cache().get(image_attrs_cache_key)

        if not image_attrs:
            if not registry_data:
                registry_data = FixuidDockerComposeAction._get_registry_data(image)
            context.log.warning("Loading attributes for image %s...", image)
            pulled_image = registry_data.pull()
            image_attrs = pulled_image.attrs
            global_cache().set(image_attrs_cache_key, image_attrs)
            context.log.success("Attributes retrieved for image %s", image)
        else:
            context.log.notice("Attributes retrieved for image %s (from cache)", image)
        return image_attrs

    @staticmethod
    def _get_image_config(image):
        if image and image != 'scratch':
            attrs = FixuidDockerComposeAction._load_image_attrs(image)
            if attrs and 'Config' in attrs:
                return attrs['Config']
        return None

    def apply_fixuid(self, service: BuildServiceDef):
        """
        Apply fixuid to given service
        """
        dockerfile_path = os.path.join(service.context, service.dockerfile)
        if os.path.exists(dockerfile_path):
            with tmp_chmod(dockerfile_path, '+w'):
                with open(dockerfile_path, "ba+") as dockerfile_file:
                    parser = CustomDockerfileParser(fileobj=dockerfile_file)

                    if FixuidDockerComposeAction._apply_fixuid_from_parser(self, parser, service):
                        context.log.success("Fixuid applied to %s",
                                            os.path.relpath(dockerfile_path, config.paths.project_home))

    def remove_fixuid(self, service: BuildServiceDef):
        """
        Remove fixuid from given service
        """
        dockerfile_path = os.path.join(service.context, service.dockerfile)
        if os.path.exists(dockerfile_path):
            with tmp_chmod(dockerfile_path, '+w'):
                with open(dockerfile_path, "ba+") as dockerfile_file:
                    parser = CustomDockerfileParser(fileobj=dockerfile_file)

                    if FixuidDockerComposeAction._remove_fixuid_from_parser(self, parser, service):
                        context.log.success("Fixuid removed from %s",
                                            os.path.relpath(dockerfile_path, config.paths.project_home))

    @staticmethod
    def _get_cmd_and_entrypoint(parser):
        entrypoint = parser.entrypoint
        cmd = parser.cmd
        # if entrypoint is defined in Dockerfile, we should not grab cmd from base image
        # and reset CMD to empty value to stay consistent with docker behavior.
        # see https://github.com/docker/docker.github.io/issues/6142
        reset_cmd = False
        if entrypoint and not cmd:
            reset_cmd = True
        if not entrypoint:
            baseimage_config = FixuidDockerComposeAction._get_image_config(parser.baseimage)
            if baseimage_config and 'Entrypoint' in baseimage_config:
                entrypoint = baseimage_config['Entrypoint']
                entrypoint = json.dumps(entrypoint)
        if not cmd and not reset_cmd:
            baseimage_config = FixuidDockerComposeAction._get_image_config(parser.baseimage)
            if baseimage_config and 'Cmd' in baseimage_config:
                cmd = baseimage_config['Cmd']
                cmd = json.dumps(cmd)
        if not cmd:
            cmd = None
        return cmd, entrypoint

    @staticmethod
    def _has_fixuid_disabled_comment(lines: Iterable[str]):
        return FixuidDockerComposeAction._has_comment(
            ['no-fixuid', 'fixuid-no', 'fixuid-disabled?', 'disabled?-fixuid'], lines)

    @staticmethod
    def _has_fixuid_manual_comment(lines: Iterable[str]):
        return FixuidDockerComposeAction._has_comment(
            ['manual-fixuid', 'fixuid-manual', 'custom-fixuid', 'fixuid-custom'], lines)

    @staticmethod
    def _has_fixuid_manual_entrypoint_comment(lines: Iterable[str]):
        return FixuidDockerComposeAction._has_comment(
            ['manual-fixuid-entrypoint',
             'fixuid-manual-entrypoint',
             'custom-fixuid-entrypoint',
             'fixuid-custom-entrypoint'], lines)

    @staticmethod
    def _has_fixuid_manual_install_comment(lines: Iterable[str]):
        return FixuidDockerComposeAction._has_comment(
            ('manual-fixuid-install',
             'fixuid-manual-install',
             'custom-fixuid-install',
             'fixuid-custom-install'), lines)

    @staticmethod
    def _has_comment(keywords: Iterable[str], lines: Iterable[str]):
        patterns = [r'^#\s*' + keyword + r'\s*$' for keyword in keywords]
        for line in lines:
            for pattern in patterns:
                if re.match(pattern, line):
                    return True
        return False

    def _apply_fixuid_from_parser(self, parser: CustomDockerfileParser, service: BuildServiceDef):
        if self._has_fixuid_disabled_comment(parser.lines):
            return False

        target = copy_from_url(config.data["fixuid.url"],
                               service.context,
                               "fixuid.tar.gz")
        if target:
            events.file.generated(source=None, target=target)

        manual_entrypoint = self._has_fixuid_manual_entrypoint_comment(parser.lines)
        manual_install = self._has_fixuid_manual_install_comment(parser.lines)
        manual = self._has_fixuid_manual_comment(parser.lines)

        ret = False
        if not manual:
            if not manual_entrypoint:
                cmd, entrypoint = FixuidDockerComposeAction._get_cmd_and_entrypoint(parser)
                fixuid_entrypoint = FixuidDockerComposeAction._add_fixuid_entrypoint(entrypoint)
                if fixuid_entrypoint:
                    parser.entrypoint = fixuid_entrypoint
                if cmd:
                    parser.cmd = cmd
                ret = True

            if not manual_install and self._dockerfile_lines[0] + "\n" not in parser.lines:
                last_instruction_user = parser.get_last_instruction("USER")
                last_instruction_entrypoint = parser.get_last_instruction("ENTRYPOINT")
                if last_instruction_user:
                    parser.add_lines_at(last_instruction_user, *self._dockerfile_lines)
                elif last_instruction_entrypoint:
                    parser.add_lines_at(last_instruction_entrypoint, *self._dockerfile_lines)
                else:
                    parser.add_lines(*self._dockerfile_lines)
                ret = True

        return ret

    def _remove_fixuid_from_parser(self, parser: CustomDockerfileParser, service: BuildServiceDef):
        baseimage_config = FixuidDockerComposeAction._get_image_config(parser.baseimage)
        image_entrypoint = None
        if baseimage_config and 'Entrypoint' in baseimage_config:
            image_entrypoint = json.dumps(baseimage_config['Entrypoint'])

        image_cmd = None
        if baseimage_config and 'Cmd' in baseimage_config:
            image_cmd = json.dumps(baseimage_config['Cmd'])

        if parser.entrypoint:
            parser.entrypoint = FixuidDockerComposeAction._remove_fixuid_entrypoint(parser.entrypoint)

        if parser.entrypoint == image_entrypoint:
            parser.entrypoint = None

        if parser.cmd == image_cmd:
            parser.cmd = None

        removed = False

        fixuid_targz = os.path.join(service.context, "fixuid.tar.gz")
        if os.path.exists(fixuid_targz):
            force_remove(fixuid_targz)
            removed = True

        lines = list(parser.lines)
        for dockerfile_line in self._dockerfile_lines:
            if dockerfile_line + "\n" in lines:
                lines.remove(dockerfile_line + "\n")
                removed = True

        if removed:
            parser.lines = lines

        return removed

    def execute(self, docker_compose_config: dict):
        """
        Execute action
        """
        self.docker_compose_config = docker_compose_config

        for service in self.get_fixuid_services():
            self.apply_fixuid(service)

    def find_fixuid_service(self, dockerfile_filepath: str, include_missing_fixuid=False):
        """
        Find related fixuid service from dockerfile filepath
        """
        for service in self.get_fixuid_services(include_missing_fixuid):
            if os.path.abspath(os.path.join(service.context, service.dockerfile)) == \
                    os.path.abspath(dockerfile_filepath):
                return service
        return None

    def get_fixuid_services(self, include_missing_fixuid=False) -> Iterable[BuildServiceDef]:
        """
        Services where fixuid.tar.gz is available in build context.
        """
        if "services" not in self.docker_compose_config:
            return

        for _, service in self.docker_compose_config.get("services").items():
            if "build" not in service.keys():
                continue

            if isinstance(service["build"], dict):
                build_context = Dotty(service).get("build.context")
            elif isinstance(service["build"], str):
                build_context = service["build"]
            else:
                continue

            if not include_missing_fixuid and not os.path.exists(os.path.join(build_context, "fixuid.yml")):
                continue

            dockerfile = Dotty(service).get("build.dockerfile", "Dockerfile")
            yield BuildServiceDef(build_context, dockerfile)

    @staticmethod
    def _parse_entrypoint(entrypoint):
        as_list = False
        start_quote = ""
        end_quote = ""

        if not entrypoint or entrypoint == "null":
            as_list = True
            entrypoint_list = []
        elif entrypoint.startswith("["):
            as_list = True
            entrypoint_list = json.loads(entrypoint)
        else:
            entrypoint_match = re.compile(r"^(['\"]?)(.*?)(['\"]?)$").match(entrypoint)
            start_quote = entrypoint_match.group(1)
            end_quote = entrypoint_match.group(3)
            entrypoint = entrypoint_match.group(2)
            entrypoint_list = shlex.split(entrypoint)

        return entrypoint_list, as_list, start_quote, end_quote

    @staticmethod
    def _add_fixuid_entrypoint(entrypoint):
        entrypoint_list, as_list, start_quote, end_quote = \
            FixuidDockerComposeAction._parse_entrypoint(entrypoint)

        fixuid_entrypoint_prefix = ["fixuid", "-q"]
        if entrypoint_list[:len(fixuid_entrypoint_prefix)] != fixuid_entrypoint_prefix:
            entrypoint_list = ["fixuid", "-q"] + entrypoint_list
        if as_list:
            entrypoint = json.dumps(entrypoint_list)
        else:
            entrypoint = " ".join(entrypoint_list)
            entrypoint = "%s%s%s" % (start_quote, entrypoint, end_quote)

        return entrypoint

    @staticmethod
    def _remove_fixuid_entrypoint(entrypoint):
        entrypoint_list, as_list, start_quote, end_quote = \
            FixuidDockerComposeAction._parse_entrypoint(entrypoint)

        fixuid_entrypoint_prefix = ["fixuid", "-q"]
        if entrypoint_list[:len(fixuid_entrypoint_prefix)] == fixuid_entrypoint_prefix:
            entrypoint_list = entrypoint_list[len(fixuid_entrypoint_prefix):]
        if as_list:
            entrypoint = json.dumps(entrypoint_list)
        else:
            entrypoint = " ".join(entrypoint_list)
            entrypoint = "%s%s%s" % (start_quote, entrypoint, end_quote)

        return entrypoint
