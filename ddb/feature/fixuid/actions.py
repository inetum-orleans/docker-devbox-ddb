# -*- coding: utf-8 -*-
import json
import os
import re
import shlex
from collections import namedtuple
from subprocess import CalledProcessError
from typing import Iterable

from chmod_monkey import tmp_chmod
from dockerfile_parse import DockerfileParser
from dotty_dict import Dotty

from ..copy.actions import copy_from_url
from ...action import Action
from ...action.action import EventBinding
from ...config import config
from ...context import context
from ...event import events
from ...utils.file import force_remove
from ...utils.process import run

BuildServiceDef = namedtuple("BuildServiceDef", "context dockerfile")


class CustomDockerfileParser(DockerfileParser):
    """
    Custom class to implement entrypoint property with the same behavior as cmd property.
    """

    def get_last_instruction(self, instruction_type, instruction_condition=lambda instruction: True):
        """
        Determine the final instruction_type instruction, if any, in the final build stage.
        instruction_types from earlier stages are ignored.
        :return: value of final stage instruction_type instruction
        """
        last_instruction = None
        for insndesc in self.structure:
            if insndesc['instruction'] == 'FROM':  # new stage, reset
                last_instruction = None
            elif insndesc['instruction'] == instruction_type and instruction_condition(insndesc):
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
        self.docker_compose_config = {}
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
    def _get_inspect_data(image):
        context.log.warning("Loading registry data id for image %s...", image)
        try:
            output = run('docker', 'inspect', '--format', '\'{{json .}}\'', image)
        except CalledProcessError:
            run('docker', 'pull', '-q', image)
            output = run('docker', 'inspect', '--format', '\'{{json .}}\'', image)
        output = output.decode().strip('\\\'\n').rstrip('\\\'\n')
        inspect_data = json.loads(output)
        context.log.info("Inspect image %s (%s)", image, inspect_data['Id'])
        return inspect_data

    @staticmethod
    def _get_image_config(image):
        if image and image != 'scratch':
            attrs = FixuidDockerComposeAction._get_inspect_data(image)
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
                entrypoint = json.dumps(baseimage_config['Entrypoint'])
        if not cmd and not reset_cmd:
            baseimage_config = FixuidDockerComposeAction._get_image_config(parser.baseimage)
            if baseimage_config and 'Cmd' in baseimage_config:
                cmd = json.dumps(baseimage_config['Cmd'])
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
                last_instruction_user = parser \
                    .get_last_instruction("USER",
                                          lambda instruction: instruction.get('value') and
                                                              instruction.get('value').lower() != 'root')
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
