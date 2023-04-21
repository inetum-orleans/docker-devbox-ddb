import os
import posixpath
import shlex
from typing import Optional, Iterable

from ddb.binary.binary import AbstractBinary
from ddb.config import config
from ddb.feature.docker.lib.compose.config.errors import ConfigurationError
from ddb.feature.docker.utils import get_mapped_path, DockerComposeControl
from ddb.utils.compat import path_as_posix_fast
from ddb.utils.process import effective_command
from ddb.utils.simpleeval import simple_eval


class DockerBinary(AbstractBinary):  # pylint:disable=too-many-instance-attributes
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
                 exe: bool = False,
                 entrypoint: Optional[str] = None,
                 global_: bool = False):
        super().__init__(name)
        self.docker_compose_service = docker_compose_service
        self.workdir = workdir
        self.options = options
        self.options_condition = options_condition
        self.condition = condition
        self.args = args
        self.exe = exe
        self.entrypoint = entrypoint
        self._global = global_

    @staticmethod
    def simple_eval_options(*args):
        """
        Retrieve the simple_eval options
        """
        return {
            "functions": {},
            "names": {
                "args": " ".join(args),
                "argv": args,
                "config": config,
                "cwd": path_as_posix_fast(config.cwd) if config.cwd else None,
                "project_cwd": path_as_posix_fast(config.project_cwd) if config.project_cwd else None
            }
        }

    def command(self, *args) -> Iterable[str]:
        cwd = config.cwd if config.cwd else os.getcwd()
        real_cwd = os.path.realpath(cwd)
        real_project_home = os.path.realpath(config.paths.project_home)
        project_relpath = os.path.relpath(config.paths.project_home, config.cwd if config.cwd else os.getcwd())

        if real_cwd.startswith(real_project_home):
            params = ["exec"] if hasattr(self, "exe") and self.exe else [
                "-f", os.path.join(project_relpath, "docker-compose.yml"),
                "run", "--rm"
            ]

            if self.workdir:
                relpath = os.path.relpath(cwd, config.paths.project_home)
                container_workdir = posixpath.join(self.workdir, relpath)
                params.append(f"--workdir={container_workdir}")
        else:
            # cwd is outside of project home.
            params = ["-f", os.path.join(project_relpath, "docker-compose.yml"), "run", "--rm"]
            if self.workdir:
                mapped_cwd = get_mapped_path(real_cwd)
                params.append(f"--volume={mapped_cwd}:{self.workdir}")
                params.append(f"--workdir={self.workdir}")

        if self.entrypoint:
            params.append(f"--entrypoint={self.entrypoint}")

        if os.environ.get('DDB_RUN_OPTS'):
            params.extend([shlex.quote(param) for param in shlex.split(os.environ.get('DDB_RUN_OPTS'))])

        self.add_options_to_params(params, self.options, self.options_condition, *args)

        params.append(self.docker_compose_service)
        if self.args:
            params.extend([shlex.quote(param) for param in shlex.split(self.args)])

        docker_compose_command = config.data.get('docker.docker_compose_command')
        if not docker_compose_command:
            raise ConfigurationError('DockerBinary requires docker feature configuration')
        command = effective_command(*shlex.split(docker_compose_command), *params)
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
        control = DockerComposeControl()
        if self.exe and not control.is_up(self.docker_compose_service):
            control.up(self.docker_compose_service)

    def should_run(self, *args) -> bool:
        if self.condition:
            return bool(simple_eval(self.condition, **self.simple_eval_options(*args)))
        return super().should_run(*args)

    @property
    def global_(self) -> bool:
        return self._global

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
        if self.condition != other.condition:
            return False
        if self.args != other.args:
            return False
        if self.exe != other.exe:
            return False
        if self.entrypoint != other.entrypoint:
            return False

        return True

    def __hash__(self):
        return hash((super().__hash__(),
                     self.docker_compose_service,
                     self.workdir,
                     self.options,
                     self.options_condition,
                     self.condition,
                     self.args,
                     self.exe,
                     self.entrypoint))
