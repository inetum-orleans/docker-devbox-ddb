import os
import posixpath
import shlex
from typing import Optional, Iterable

from simpleeval import simple_eval

from ddb.binary import Binary
from ddb.config import config
from ddb.utils.process import effective_command


class DockerBinary(Binary):
    """
    Binary to run docker compose command.
    """

    def __init__(self,
                 name: str,
                 docker_compose_service: str,
                 workdir: Optional[str] = None,
                 options: Optional[str] = None,
                 options_condition: Optional[str] = None,
                 args: Optional[str] = None,
                 exe: bool = False):
        self._name = name
        self.docker_compose_service = docker_compose_service
        self.workdir = workdir
        self.options = options
        self.options_condition = options_condition
        self.args = args
        self.exe = exe

    @property
    def name(self) -> str:
        return self._name

    def command(self, *args) -> Iterable[str]:
        params = ["exec" if hasattr(self, 'exe') and self.exe else "run"]

        if self.workdir:
            relpath = os.path.relpath(os.getcwd(), config.paths.project_home)
            container_workdir = posixpath.join(self.workdir, relpath)
            params.append("--workdir=%s" % (container_workdir,))

        self.add_options_to_params(params, self.options, self.options_condition, args)

        params.append(self.docker_compose_service)
        if self.args:
            params.extend(shlex.split(self.args))

        command = effective_command("docker-compose", *params)
        return command

    def add_options_to_params(self, params, options, condition, args=()):  # pylint: disable=no-self-use
        """
        Add options to params if condition is fulfilled
        :param params: the list of parameters
        :param options: options to add
        :param condition: the condition to fulfilled
        :param args: the list of args of binary call
        :return:
        """
        if condition is not None and options is not None:
            if simple_eval(condition, functions={}, names={'args': args}):
                params.extend(shlex.split(options))
        else:
            if options is not None:
                params.extend(shlex.split(options))

    def is_same(self, binary) -> bool:
        """
        Check if given binary is the same as the current one
        :param binary:
        :return: True or False depending on it's the same or not
        """
        if not isinstance(binary, DockerBinary):
            return False
        if self.command() != binary.command():
            return False
        if self.options != binary.options:
            return False
        if self.options_condition != binary.options_condition:
            return False
        return True
