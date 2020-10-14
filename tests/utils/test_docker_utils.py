import os
import sys

import yaml

from ddb.utils.docker import DockerUtils, DockerComposeYamlMissingException


class TestDockerUtils:
    def test_get_config(self, data_dir: str):
        os.chdir(data_dir)

        yaml_config = DockerUtils.get_config()

        assert os.path.exists('docker-compose.yml')
        with open('docker-compose.yml', 'r') as f:
            expected = yaml.load(f.read(), yaml.SafeLoader)

        assert expected == yaml_config

    def test_basic_manipulations(self, data_dir: str):
        container_name = 'web'
        os.chdir(data_dir)
        DockerUtils.service_stop(container_name)

        assert not DockerUtils.is_container_up(container_name)

        DockerUtils.service_up(container_name)

        assert DockerUtils.is_container_up(container_name)
        DockerUtils.service_stop(container_name)

        assert not DockerUtils.is_container_up(container_name)
