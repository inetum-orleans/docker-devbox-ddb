import os
import posixpath
import shlex
from typing import Optional, Iterable

from simpleeval import simple_eval

from pathlib import Path

from ddb.binary.binary import AbstractBinary
from ddb.config import config
from ddb.utils.docker import DockerUtils
from ddb.utils.process import effective_command


class DockerBinary(AbstractBinary):
    """
    Binary to run docker compose command.
    """

    def __init__(self,
                 name: str,
                 docker_compose_service: str,
                 workdir: Optional[str] = None,
                 options: Optional[str] = None,
                 options_condition: Optional[str] = None,
                 condition: Optional[str] = None,
                 args: Optional[str] = None,
                 exe: bool = False):
        super().__init__(name)
        self.docker_compose_service = docker_compose_service
        self.workdir = workdir
        self.options = options
        self.options_condition = options_condition
        self.condition = condition
        self.args = args
        self.exe = exe

    @staticmethod
    def simple_eval_options(*args):
        """
        Retrieve the simple_eval options
        """
        return dict(functions={},
                    names={'args': ' '.join(args),
                           'argv': args,
                           'config': config,
                           'cwd': str(Path(config.cwd).as_posix()) if config.cwd else None,
                           'project_cwd': str(Path(config.project_cwd).as_posix()) if config.project_cwd else None})

    def command(self, *args) -> Iterable[str]:
        params = ["exec"] if hasattr(self, 'exe') and self.exe else ["run", "--rm"]

        if self.workdir:
            relpath = os.path.relpath(config.cwd if config.cwd else os.getcwd(), config.paths.project_home)
            container_workdir = posixpath.join(self.workdir, relpath)
            params.append("--workdir=%s" % (container_workdir,))

        self.add_options_to_params(params, self.options, self.options_condition, *args)

        params.append(self.docker_compose_service)
        if self.args:
            params.extend(shlex.split(self.args))

        command = effective_command("docker-compose", *params)
        return command

    def add_options_to_params(self, params, options, condition, *args):
        """
        Add options to params if condition is fulfilled
        :param params: the list of parameters
        :param options: options to add
        :param condition: the condition to fulfilled
        :param args: the list of args of binary call
        :return:
        """
        if condition is not None and options is not None:
            if simple_eval(condition, **self.simple_eval_options(*args)):
                params.extend(shlex.split(options))
        else:
            if options is not None:
                params.extend(shlex.split(options))

    def before_run(self, *args):
        if self.exe and not DockerUtils.is_container_up(self.docker_compose_service):
            DockerUtils.service_up(self.docker_compose_service)

    def should_run(self, *args) -> bool:
        if self.condition:
            return bool(simple_eval(self.condition, **self.simple_eval_options(*args)))
        return super().should_run(*args)

    def __lt__(self, other):
        """
        This is used to order binaries in run feature action.
        """
        if not isinstance(other, DockerBinary):
            return True
        return self.condition and not other.condition

    def __gt__(self, other):
        """
        This is used to order binaries in run feature action.
        """
        if not isinstance(other, DockerBinary):
            return False
        return not self.condition and other.condition

    def __eq__(self, other):  # pylint:disable=too-many-return-statements
        """
        Check if given binary is the same as the current one
        :param binary:
        :return: True or False depending on it's the same or not
        """
        if not super().__eq__(other):
            return False
        if not isinstance(other, DockerBinary):
            return False
        if self.docker_compose_service != other.docker_compose_service:
            return False
        if self.workdir != other.workdir:
            return False
        if self.options != other.options:
            return False
        if self.options_condition != other.options_condition:
            return False
        if self.args != other.args:
            return False
        if self.exe != other.exe:
            return False

        return True

    def __hash__(self):
        return hash((super().__hash__(),
                     self.docker_compose_service,
                     self.workdir,
                     self.options,
                     self.options_condition,
                     self.args,
                     self.exe))
