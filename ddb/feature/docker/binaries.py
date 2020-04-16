import os
import posixpath
import shlex
from typing import Optional, List

from ddb.binary import Binary
from ddb.config import config


class DockerBinary(Binary):
    """
    Binary to run docker compose command.
    """

    def __init__(self,
                 name: str,
                 docker_compose_service: str,
                 workdir: Optional[str] = None,
                 options: Optional[str] = None,
                 args: Optional[str] = None):
        self._name = name
        self.docker_compose_service = docker_compose_service
        self.workdir = workdir
        self.options = options
        self.args = args

    @property
    def name(self) -> str:
        return self._name

    def command(self, *args) -> List[str]:
        params = ["run"]

        if self.workdir:
            relpath = os.path.relpath(os.getcwd(), config.paths.project_home)
            container_workdir = posixpath.join(self.workdir, relpath)
            params.append("--workdir=%s" % (container_workdir,))
        if self.options:
            params.extend(shlex.split(self.options))
        params.append(self.docker_compose_service)
        if self.args:
            params.extend(shlex.split(self.args))

        docker_compose_bin = config.data["docker.compose.bin"]
        docker_compose_args = config.data.get("docker.compose.args", [])
        command = [docker_compose_bin] + docker_compose_args + list(params) + list(args)
        return command
