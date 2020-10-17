import os
import yaml

from ddb.utils.process import run


class DockerUtils:
    """
    A set of tools to manipulate docker using docker and docker-compose system commands
    """

    @staticmethod
    def service_up(name: str = None):
        """
        Execute docker-compose up -d
        :param name: the name of a specific service to up
        :raise DockerComposeYamlMissingException: in case of missing docker-compose.yml in folder
        :return:
        """
        if not os.path.exists("docker-compose.yml"):
            raise DockerComposeYamlMissingException
        if name is None:
            run("docker-compose", "up", "-d")
        else:
            run("docker-compose", "up", "-d", name)

    @staticmethod
    def service_stop(name: str):
        """
        Execute docker-compose stop
        :param name: the name of a specific service to stop
        :raise DockerComposeYamlMissingException: in case of missing docker-compose.yml in folder
        :return:
        """
        if not os.path.exists("docker-compose.yml"):
            raise DockerComposeYamlMissingException
        if name is None:
            run("docker-compose", "stop")
        else:
            run("docker-compose", "stop", name)

    @staticmethod
    def is_container_up(name: str):
        """
        Check if the given service is up.
        :param name: The name of the container to check
        :raise DockerComposeYamlMissingException: in case of missing docker-compose.yml in folder
        :return:
        """
        if not os.path.exists("docker-compose.yml"):
            raise DockerComposeYamlMissingException
        container_id = run("docker-compose", "ps", "-q", name).decode("utf-8").rstrip()
        if len(container_id) == 0:
            return False
        containers = run('docker', 'ps', '-q', '--no-trunc').decode("utf-8").rstrip().split('\n')
        return container_id in containers

    @staticmethod
    def get_config():
        """
        Get the docker-compose.yml configuration content.
        :raise DockerComposeYamlMissingException: in case of missing docker-compose.yml
        :return:
        """
        if not os.path.exists("docker-compose.yml"):
            raise DockerComposeYamlMissingException

        config = run("docker-compose", "config")
        return yaml.load(config, yaml.SafeLoader)


class DockerComposeYamlMissingException(Exception):
    """
    Exception raised in case of missing docker-compose file.
    """

    def __init__(self):
        Exception.__init__()
        self.message = "There is no docker-compose.yml file in current folder ({})".format(os.getcwd())
