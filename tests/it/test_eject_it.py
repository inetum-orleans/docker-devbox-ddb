import os

import yaml
import pytest

from ddb.__main__ import main
from tests.utilstest import expect_gitignore, setup_cfssl


class TestEject:
    @pytest.mark.docker
    def test_eject1(self, project_loader, module_scoped_container_getter):
        project_loader("eject1")

        setup_cfssl(module_scoped_container_getter)

        main(["configure"])

        assert os.path.exists("docker-compose.yml")
        assert os.path.exists("docker-compose.yml.jsonnet")
        assert expect_gitignore(".gitignore", "/docker-compose.yml")

        assert os.path.exists(os.path.join(".bin", "psql" + (".bat" if os.name == "nt" else "")))
        assert expect_gitignore(".gitignore", "/.bin/psql" + (".bat" if os.name == "nt" else ""))

        assert os.path.exists(os.path.join(".docker", "db", "Dockerfile.jinja"))
        assert expect_gitignore(".gitignore", "/.docker/db/Dockerfile")

        main(["configure", "--eject"])

        assert os.path.exists("docker-compose.yml")
        assert not os.path.exists("docker-compose.yml.jsonnet")
        assert not expect_gitignore(".gitignore", "/docker-compose.yml")

        assert os.path.exists(os.path.join(".bin", "psql" + (".bat" if os.name == "nt" else "")))
        assert expect_gitignore(".gitignore", "/.bin/psql" + (".bat" if os.name == "nt" else ""))

        assert not os.path.exists(os.path.join(".docker", "db", "Dockerfile.jinja"))
        assert not expect_gitignore(".gitignore", "/.docker/db/Dockerfile")

        with open('docker-compose.yml', 'r') as dc_file:
            data = yaml.load(dc_file, yaml.SafeLoader)

        with open('../expected/docker-compose.yml', 'r') as expected_dc_file:
            expected_data = yaml.load(expected_dc_file, yaml.SafeLoader)

        assert data == expected_data

    @pytest.mark.docker
    def test_eject2(self, project_loader, module_scoped_container_getter):
        project_loader("eject2")

        setup_cfssl(module_scoped_container_getter)

        main(["configure"])

        assert os.path.exists("docker-compose.yml")
        assert os.path.exists("docker-compose.yml.jsonnet")
        assert expect_gitignore(".gitignore", "/docker-compose.yml")

        assert os.path.exists(os.path.join(".bin", "psql" + (".bat" if os.name == "nt" else "")))
        assert expect_gitignore(".gitignore", "/.bin/psql" + (".bat" if os.name == "nt" else ""))

        assert os.path.exists(os.path.join(".docker", "db", "Dockerfile.jinja"))
        assert expect_gitignore(".gitignore", "/.docker/db/Dockerfile")

        main(["configure", "--eject"])

        assert os.path.exists("docker-compose.yml")
        assert not os.path.exists("docker-compose.yml.jsonnet")
        assert not expect_gitignore(".gitignore", "/docker-compose.yml")

        assert os.path.exists(os.path.join(".bin", "psql" + (".bat" if os.name == "nt" else "")))
        assert expect_gitignore(".gitignore", "/.bin/psql" + (".bat" if os.name == "nt" else ""))

        assert not os.path.exists(os.path.join(".docker", "db", "Dockerfile.jinja"))
        assert not expect_gitignore(".gitignore", "/.docker/db/Dockerfile")

        with open('docker-compose.yml', 'r') as dc_file:
            data = yaml.load(dc_file, yaml.SafeLoader)

        with open('../expected/docker-compose.yml', 'r') as expected_dc_file:
            expected_data = yaml.load(expected_dc_file, yaml.SafeLoader)

        assert data == expected_data

    @pytest.mark.docker
    def test_eject2_with_jsonnet_disabled(self, project_loader, module_scoped_container_getter):
        project_loader("eject2")

        setup_cfssl(module_scoped_container_getter)

        main(["configure"])

        assert os.path.exists("docker-compose.yml")
        assert os.path.exists("docker-compose.yml.jsonnet")
        assert expect_gitignore(".gitignore", "/docker-compose.yml")

        assert os.path.exists(os.path.join(".bin", "psql" + (".bat" if os.name == "nt" else "")))
        assert expect_gitignore(".gitignore", "/.bin/psql" + (".bat" if os.name == "nt" else ""))

        assert os.path.exists(os.path.join(".docker", "db", "Dockerfile.jinja"))
        assert expect_gitignore(".gitignore", "/.docker/db/Dockerfile")

        os.environ['DDB_OVERRIDE_JSONNET_DOCKER_VIRTUALHOST_DISABLED'] = "1"
        os.environ['DDB_OVERRIDE_JSONNET_DOCKER_BINARY_DISABLED'] = "True"
        main(["configure", "--eject"])

        assert os.path.exists("docker-compose.yml")
        assert not os.path.exists("docker-compose.yml.jsonnet")
        assert not expect_gitignore(".gitignore", "/docker-compose.yml")

        assert not os.path.exists(os.path.join(".bin", "psql" + (".bat" if os.name == "nt" else "")))
        assert not expect_gitignore(".gitignore", "/.bin/psql" + (".bat" if os.name == "nt" else ""))

        assert not os.path.exists(os.path.join(".docker", "db", "Dockerfile.jinja"))
        assert not expect_gitignore(".gitignore", "/.docker/db/Dockerfile")

        with open('docker-compose.yml', 'r') as dc_file:
            data = yaml.load(dc_file, yaml.SafeLoader)

        with open('../expected/docker-compose.jsonnet.disabled.yml', 'r') as expected_dc_file:
            expected_data = yaml.load(expected_dc_file, yaml.SafeLoader)

        assert data == expected_data

    def test_eject3(self, project_loader):
        project_loader("eject3")

        main(["configure"])

        assert os.path.exists("../home/test.txt")
        assert os.path.exists(".docker/c1/test.txt")
        assert os.path.exists(".docker/c2/test.txt")
        assert os.path.exists("config.jinja.txt")
        assert os.path.exists("config.txt")

        main(["configure", "--eject"])

        assert os.path.exists("../home/test.txt")
        assert os.path.exists(".docker/c1/test.txt")
        assert os.path.exists(".docker/c2/test.txt")
        assert not os.path.exists("config.jinja.txt")
        assert os.path.exists("config.txt")
