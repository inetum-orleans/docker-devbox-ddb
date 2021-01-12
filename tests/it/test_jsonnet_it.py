import os

import pytest
import yaml

from ddb.__main__ import main


class TestJsonnet:
    def test_jsonnet_ext_var(self, project_loader):
        project_loader("jsonnet-extvar")

        main(["configure"])

        assert os.path.exists('config.yml')
        with open('config.yml', 'r') as f:
            variables = f.read()

        with open('config.expected.yml', 'r') as f:
            variables_expected = f.read()

        assert variables == variables_expected


class TestDockerJsonnet:
    @pytest.mark.skipif("os.name == 'nt'")
    def test_named_user_group(self, project_loader):
        project_loader("named-user-group")

        main(["configure"])

        assert os.path.exists('docker-compose.yml')
        with open('docker-compose.yml', 'r') as f:
            docker_compose = yaml.load(f, yaml.SafeLoader)

        with open('docker-compose.expected.yml', 'r') as f:
            docker_compose_expected = yaml.load(f, yaml.SafeLoader)

        assert docker_compose == docker_compose_expected

    def test_named_invalid_user_group(self, project_loader):
        project_loader("named-invalid-user-group")

        with pytest.raises(RuntimeError):
            main(["configure"])

    def test_binary(self, project_loader):
        project_loader("jsonnet-binary")

        main(["configure"])

        assert os.path.exists('docker-compose.yml')
        with open('docker-compose.yml', 'r') as f:
            docker_compose = yaml.load(f, yaml.SafeLoader)

        with open('docker-compose.expected.yml', 'r') as f:
            docker_compose_expected = yaml.load(f, yaml.SafeLoader)

        assert docker_compose == docker_compose_expected
