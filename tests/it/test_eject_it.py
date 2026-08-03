import os
from pathlib import Path

import pytest
import yaml

from ddb.__main__ import main
from ddb.config import config
from tests.utilstest import expect_gitignore, setup_cfssl


class TestEject:
    @pytest.mark.docker
    def test_eject1(self, project_loader, module_scoped_container_getter):
        project_loader("eject1")

        setup_cfssl(module_scoped_container_getter)

        main(["configure"])

        assert Path("docker-compose.yml").exists()
        assert Path("docker-compose.yml.jsonnet").exists()
        assert expect_gitignore(".gitignore", "/docker-compose.yml")

        assert (Path(".bin") / ("psql" + (".bat" if os.name == "nt" else ""))).exists()
        assert expect_gitignore(".gitignore", "/.bin/psql" + (".bat" if os.name == "nt" else ""))

        assert (Path(".docker") / "db" / "Dockerfile.jinja").exists()
        assert expect_gitignore(".gitignore", "/.docker/db/Dockerfile")

        main(["configure", "--eject"], reset_disabled=True)

        assert Path("docker-compose.yml").exists()
        assert not Path("docker-compose.yml.jsonnet").exists()
        assert not expect_gitignore(".gitignore", "/docker-compose.yml")

        assert (Path(".bin") / ("psql" + (".bat" if os.name == "nt" else ""))).exists()
        assert expect_gitignore(".gitignore", "/.bin/psql" + (".bat" if os.name == "nt" else ""))

        assert not (Path(".docker") / "db" / "Dockerfile.jinja").exists()
        assert not expect_gitignore(".gitignore", "/.docker/db/Dockerfile")

        with Path("docker-compose.yml").open() as dc_file:
            actual = yaml.load(dc_file, yaml.SafeLoader)

        with Path("../expected/docker-compose.yml").open() as expected_dc_file:
            expected_data = expected_dc_file.read()
            expected_data = expected_data.replace(
                "%network_name%", str(config.data.get("jsonnet.docker.compose.network_name"))
            )
            expected = yaml.load(expected_data, yaml.SafeLoader)

        assert actual == expected

    @pytest.mark.docker
    def test_eject2(self, project_loader, module_scoped_container_getter):
        project_loader("eject2")

        setup_cfssl(module_scoped_container_getter)

        main(["configure"])

        assert Path("docker-compose.yml").exists()
        assert Path("docker-compose.yml.jsonnet").exists()
        assert expect_gitignore(".gitignore", "/docker-compose.yml")

        assert (Path(".bin") / ("psql" + (".bat" if os.name == "nt" else ""))).exists()
        assert expect_gitignore(".gitignore", "/.bin/psql" + (".bat" if os.name == "nt" else ""))

        assert (Path(".docker") / "db" / "Dockerfile.jinja").exists()
        assert expect_gitignore(".gitignore", "/.docker/db/Dockerfile")

        main(["configure", "--eject"], reset_disabled=True)

        assert Path("docker-compose.yml").exists()
        assert not Path("docker-compose.yml.jsonnet").exists()
        assert not expect_gitignore(".gitignore", "/docker-compose.yml")

        assert (Path(".bin") / ("psql" + (".bat" if os.name == "nt" else ""))).exists()
        assert expect_gitignore(".gitignore", "/.bin/psql" + (".bat" if os.name == "nt" else ""))

        assert not (Path(".docker") / "db" / "Dockerfile.jinja").exists()
        assert not expect_gitignore(".gitignore", "/.docker/db/Dockerfile")

        with Path("docker-compose.yml").open() as dc_file:
            actual = yaml.load(dc_file, yaml.SafeLoader)

        with Path("../expected/docker-compose.yml").open() as expected_dc_file:
            expected_data = expected_dc_file.read()
            expected_data = expected_data.replace(
                "%network_name%", str(config.data.get("jsonnet.docker.compose.network_name"))
            )
            expected = yaml.load(expected_data, yaml.SafeLoader)

        assert actual == expected

    @pytest.mark.docker
    def test_eject2_with_jsonnet_disabled(self, project_loader, module_scoped_container_getter):
        project_loader("eject2")

        setup_cfssl(module_scoped_container_getter)

        main(["configure"])

        assert Path("docker-compose.yml").exists()
        assert Path("docker-compose.yml.jsonnet").exists()
        assert expect_gitignore(".gitignore", "/docker-compose.yml")

        assert (Path(".bin") / ("psql" + (".bat" if os.name == "nt" else ""))).exists()
        assert expect_gitignore(".gitignore", "/.bin/psql" + (".bat" if os.name == "nt" else ""))

        assert (Path(".docker") / "db" / "Dockerfile.jinja").exists()
        assert expect_gitignore(".gitignore", "/.docker/db/Dockerfile")

        os.environ["DDB_OVERRIDE_JSONNET_DOCKER_VIRTUALHOST_DISABLED"] = "1"
        os.environ["DDB_OVERRIDE_JSONNET_DOCKER_BINARY_DISABLED"] = "True"
        main(["configure", "--eject"], reset_disabled=True)

        assert Path("docker-compose.yml").exists()
        assert not Path("docker-compose.yml.jsonnet").exists()
        assert not expect_gitignore(".gitignore", "/docker-compose.yml")

        assert not (Path(".bin") / ("psql" + (".bat" if os.name == "nt" else ""))).exists()
        assert not expect_gitignore(".gitignore", "/.bin/psql" + (".bat" if os.name == "nt" else ""))

        assert not (Path(".docker") / "db" / "Dockerfile.jinja").exists()
        assert not expect_gitignore(".gitignore", "/.docker/db/Dockerfile")

        with Path("docker-compose.yml").open() as dc_file:
            actual = yaml.load(dc_file, yaml.SafeLoader)

        with Path("../expected/docker-compose.jsonnet.disabled.yml").open() as expected_dc_file:
            expected_data = expected_dc_file.read()
            expected_data = expected_data.replace(
                "%network_name%", str(config.data.get("jsonnet.docker.compose.network_name"))
            )
            expected = yaml.load(expected_data, yaml.SafeLoader)

        assert actual == expected

    def test_eject3(self, project_loader):
        project_loader("eject3")

        main(["configure"])

        assert Path("../home/test.txt").exists()
        assert Path(".docker/c1/test.txt").exists()
        assert Path(".docker/c2/test.txt").exists()
        assert Path("config.jinja.txt").exists()
        assert Path("config.txt").exists()

        main(["configure", "--eject"])

        assert Path("../home/test.txt").exists()
        assert Path(".docker/c1/test.txt").exists()
        assert Path(".docker/c2/test.txt").exists()
        assert not Path("config.jinja.txt").exists()
        assert Path("config.txt").exists()
