from pathlib import Path

import pytest
import yaml
from dotty_dict import Dotty

from ddb.__main__ import main
from ddb.config import config
from tests.utilstest import get_group_gid, get_user_uid_gid


class TestJsonnet:
    def test_jsonnet_ext_var(self, project_loader):
        project_loader("jsonnet-extvar")

        main(["configure"])

        assert Path("config.yml").exists()
        with Path("config.yml").open() as f:
            variables = f.read()

        with Path("config.expected.yml").open() as f:
            variables_expected = f.read()

        assert variables == variables_expected


class TestDockerJsonnet:
    @pytest.mark.skipif("os.name == 'nt'")
    def test_named_user_group(self, project_loader):
        project_loader("named-user-group")

        main(["configure"], reset_disabled=True)

        assert Path("docker-compose.yml").exists()
        with Path("docker-compose.yml").open() as f:
            docker_compose = yaml.load(f, yaml.SafeLoader)

        with Path("docker-compose.expected.yml").open() as f:
            expected_data = f.read()
            expected_data = expected_data.replace(
                "%network_name%", str(config.data.get("jsonnet.docker.compose.network_name"))
            )
            docker_compose_expected = yaml.load(expected_data, yaml.SafeLoader)

        uid, _ = get_user_uid_gid("root")
        gid = get_group_gid("nobody")

        Dotty(docker_compose_expected)["services.maven.user"] = f"{uid}:{gid}"

        assert docker_compose == docker_compose_expected

    def test_named_invalid_user_group(self, project_loader):
        project_loader("named-invalid-user-group")

        with pytest.raises(RuntimeError):
            main(["configure"])

    def test_binary(self, project_loader):
        project_loader("jsonnet-binary")

        main(["configure"], reset_disabled=True)

        assert Path("docker-compose.yml").exists()
        with Path("docker-compose.yml").open() as f:
            docker_compose = yaml.load(f, yaml.SafeLoader)

        with Path("docker-compose.expected.yml").open() as f:
            expected_data = f.read()
            expected_data = expected_data.replace(
                "%network_name%", str(config.data.get("jsonnet.docker.compose.network_name"))
            )

            docker_compose_expected = yaml.load(expected_data, yaml.SafeLoader)

        assert docker_compose == docker_compose_expected

    def test_resolve_ports_conflicts(self, project_loader):
        project_loader("jsonnet-resolve-ports-conflicts")

        main(["configure"], reset_disabled=True)

        assert Path("docker-compose.yml").exists()
        with Path("docker-compose.yml").open() as f:
            docker_compose = yaml.safe_load(f)

        with Path("docker-compose.expected.yml").open() as f:
            expected_data = f.read()
            expected_data = expected_data.replace(
                "%network_name%", str(config.data.get("jsonnet.docker.compose.network_name"))
            )

            docker_compose_expected = yaml.load(expected_data, yaml.SafeLoader)

        assert docker_compose == docker_compose_expected
