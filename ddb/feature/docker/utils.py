import os
import shlex
from subprocess import CalledProcessError

import yaml

from ddb.config import config
from ddb.feature.docker.lib.compose.config.errors import ConfigurationError
from ddb.utils.process import run


def get_mapped_path(path: str):
    """
    Get docker mapped path, using `docker.path_mapping` configuration.
    :param path:
    :return:
    """
    path_mapping = config.data.get('docker.path_mapping')
    fixed_path = None
    fixed_source_path = None
    if path_mapping:
        for source_path, target_path in path_mapping.items():
            if path.startswith(source_path) and \
                    (not fixed_source_path or len(source_path) > len(fixed_source_path)):
                fixed_source_path = source_path
                fixed_path = target_path + path[len(source_path):]
    return fixed_path if fixed_path else path


class DockerComposeControl:
    """
    A set of tools to manipulate docker using docker and docker-compose system commands
    """

    def __init__(self):
        docker_command = config.data.get("docker.docker_command")
        docker_compose_command = config.data.get("docker.docker_compose_command")

        if not docker_command or not docker_compose_command:
            raise ConfigurationError('DockerComposeControl requires docker feature configuration')

        self.docker_command = shlex.split(docker_command)
        self.docker_compose_command = shlex.split(docker_compose_command)

    def up(self, name: str = None):  # pylint:disable=invalid-name
        """
        Execute docker-compose up -d
        :param name: the name of a specific service to up
        :raise DockerComposeYamlMissingException: in case of missing docker-compose.yml in folder
        :return:
        """
        if not os.path.exists("docker-compose.yml"):
            raise DockerComposeYamlMissingException
        if name is None:
            run(*self.docker_compose_command, "up", "-d")
        else:
            run(*self.docker_compose_command, "up", "-d", name)

    def stop(self, name: str):
        """
        Execute docker-compose stop
        :param name: the name of a specific service to stop
        :raise DockerComposeYamlMissingException: in case of missing docker-compose.yml in folder
        :return:
        """
        if not os.path.exists("docker-compose.yml"):
            raise DockerComposeYamlMissingException
        if name is None:
            run(*self.docker_compose_command, "stop")
        else:
            run(*self.docker_compose_command, "stop", name)

    def start(self, name: str):
        """
        Execute docker-compose start
        :param name: the name of a specific service to start
        :raise DockerComposeYamlMissingException: in case of missing docker-compose.yml in folder
        :return:
        """
        if not os.path.exists("docker-compose.yml"):
            raise DockerComposeYamlMissingException
        if name is None:
            run(*self.docker_compose_command, "start")
        else:
            run(*self.docker_compose_command, "start", name)

    def down(self):
        """
        Execute docker-compose down
        :param name: the name of a specific service to stop
        :raise DockerComposeYamlMissingException: in case of missing docker-compose.yml in folder
        :return:
        """
        if not os.path.exists("docker-compose.yml"):
            raise DockerComposeYamlMissingException
        run(*self.docker_compose_command, "down")

    def is_up(self, name: str):
        """
        Check if the given service is up.
        :param name: The name of the container to check
        :raise DockerComposeYamlMissingException: in case of missing docker-compose.yml in folder
        :return:
        """
        if not os.path.exists("docker-compose.yml"):
            raise DockerComposeYamlMissingException
        try:
            container_id = run(*self.docker_compose_command, "ps", "-q", name).decode("utf-8").rstrip()
        except CalledProcessError as err:
            if b'no such service' in err.stderr:
                return False
            raise
        if len(container_id) == 0:
            return False
        containers = run(*self.docker_command, 'ps', '-q', '--no-trunc').decode("utf-8").rstrip().split('\n')
        return container_id in containers

    def config(self, parse=True):
        """
        Get the docker-compose.yml configuration content.
        :raise DockerComposeYamlMissingException: in case of missing docker-compose.yml
        :return:
        """
        if not os.path.exists("docker-compose.yml"):
            raise DockerComposeYamlMissingException

        compose_config = run(*self.docker_compose_command, "config")
        if parse:
            return yaml.load(compose_config, yaml.SafeLoader)
        return compose_config


class DockerComposeYamlMissingException(Exception):
    """
    Exception raised in case of missing docker-compose file.
    """

    def __init__(self):
        super().__init__()
        self.message = "There is no docker-compose.yml file in current folder ({})".format(os.getcwd())
