import os
from pathlib import Path

import pytest
import yaml

from ddb.__main__ import load_registered_features, register_actions_in_event_bus
from ddb.config import config, migrations
from ddb.config.migrations import PropertyMigration
from ddb.feature import features
from ddb.feature.core import CoreFeature
from ddb.feature.docker import DockerFeature
from ddb.feature.file import FileFeature, FileWalkAction
from ddb.feature.jsonnet import JsonnetFeature
from ddb.utils.compat import path_as_posix_fast


class TestJsonnetAction:
    def test_empty_project_without_core(self, project_loader):
        project_loader("empty")

        features.register(FileFeature())
        features.register(JsonnetFeature())
        load_registered_features()
        register_actions_in_event_bus(fail_fast=True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

    def test_empty_project_with_core(self, project_loader):
        project_loader("empty")

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(JsonnetFeature())
        load_registered_features()
        register_actions_in_event_bus(fail_fast=True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

    @pytest.mark.skipif("os.name == 'nt'")
    def test_named_user_group(self, project_loader):
        project_loader("empty")

        features.register(JsonnetFeature())
        load_registered_features()

        assert config.data.get("jsonnet.docker.user.name_to_uid")
        assert config.data.get("jsonnet.docker.user.group_to_gid")

    @pytest.mark.skipif("os.name != 'nt'")
    def test_named_user_group_windows(self, project_loader):
        project_loader("empty")

        features.register(JsonnetFeature())
        load_registered_features()

        assert config.data.get("jsonnet.docker.user.name_to_uid") == {}
        assert config.data.get("jsonnet.docker.user.group_to_gid") == {}

    def test_example1(self, project_loader):
        project_loader("example1")

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(JsonnetFeature())
        load_registered_features()
        register_actions_in_event_bus(fail_fast=True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert Path("example1.json").exists()
        with Path("example1.json").open() as f:
            example = f.read()

        with Path("example1.expected.json").open() as f:
            example_expected = f.read()

        assert example == example_expected

    def test_example1_yaml(self, project_loader):
        project_loader("example1.yaml")

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(JsonnetFeature())
        load_registered_features()
        register_actions_in_event_bus(fail_fast=True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert Path("example1.another").exists()
        with Path("example1.another").open() as f:
            example_another = f.read()

        with Path("example1.expected.another").open() as f:
            example_another_expected = f.read()

        assert example_another == example_another_expected

        assert Path("example1.yaml").exists()
        with Path("example1.yaml").open() as f:
            example_yaml = f.read()

        with Path("example1.expected.yaml").open() as f:
            example_yaml_expected = f.read()

        assert example_yaml == example_yaml_expected

    def test_example2(self, project_loader):
        project_loader("example2")

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(JsonnetFeature())
        load_registered_features()
        register_actions_in_event_bus(fail_fast=True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert Path("example2.json").exists()
        with Path("example2.json").open() as f:
            example = f.read()

        with Path("example2.expected.json").open() as f:
            example_expected = f.read()

        assert example == example_expected

    def test_example3(self, project_loader):
        project_loader("example3")

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(JsonnetFeature())
        load_registered_features()
        register_actions_in_event_bus(fail_fast=True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert Path("uwsgi.ini").exists()
        with Path("uwsgi.ini").open() as f:
            iwsgi = f.read()

        with Path("uwsgi.expected.ini").open() as f:
            iwsgi_expected = f.read()

        assert iwsgi == iwsgi_expected

        assert Path("init.sh").exists()
        with Path("init.sh").open() as f:
            init = f.read()

        with Path("init.expected.sh").open() as f:
            init_expected = f.read()

        assert init == init_expected

        assert Path("cassandra.conf").exists()
        with Path("cassandra.conf").open() as f:
            cassandra = f.read()

        with Path("cassandra.expected.conf").open() as f:
            cassandra_expected = f.read()

        assert cassandra == cassandra_expected

    def test_example3_with_dir(self, project_loader):
        project_loader("example3.with_dir")

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(JsonnetFeature())
        load_registered_features()
        register_actions_in_event_bus(fail_fast=True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert Path("./target/uwsgi.ini").exists()
        with Path("./target/uwsgi.ini").open() as f:
            iwsgi = f.read()

        with Path("uwsgi.expected.ini").open() as f:
            iwsgi_expected = f.read()

        assert iwsgi == iwsgi_expected

        assert Path("./target/init.sh").exists()
        with Path("./target/init.sh").open() as f:
            init = f.read()

        with Path("init.expected.sh").open() as f:
            init_expected = f.read()

        assert init == init_expected

        assert Path("./target/cassandra.conf").exists()
        with Path("./target/cassandra.conf").open() as f:
            cassandra = f.read()

        with Path("cassandra.expected.conf").open() as f:
            cassandra_expected = f.read()

        assert cassandra == cassandra_expected

    def test_config_variables(self, project_loader):
        project_loader("config_variables")

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(JsonnetFeature())
        load_registered_features()
        register_actions_in_event_bus(fail_fast=True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert Path("variables.json").exists()
        with Path("variables.json").open() as f:
            variables = f.read()

        with Path("variables.expected.json").open() as f:
            variables_expected = f.read()

        assert variables == variables_expected

    @pytest.mark.parametrize(
        "variant",
        [
            "test-dev",
            "test-ci",
            "test-stage",
            "test-prod",
        ],
    )
    def test_docker_compose_traefik(self, project_loader, variant):
        def before_load_config():
            Path(f"ddb.{variant}.yml").rename("ddb.yml")
            Path(f"docker-compose.expected.{variant}.yml").rename("docker-compose.expected.yml")

        project_loader("docker_compose_traefik", before_load_config)

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(DockerFeature())
        features.register(JsonnetFeature())
        load_registered_features()
        register_actions_in_event_bus(fail_fast=True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert Path("docker-compose.yml").exists()
        with Path("docker-compose.yml").open() as f:
            rendered = yaml.load(f.read(), yaml.SafeLoader)

        with Path("docker-compose.expected.yml").open() as f:
            expected_data = f.read()

            if os.name == "nt":
                expected_data = expected_data.replace("%ddb.path.project%", path_as_posix_fast(str(Path.cwd())))
            else:
                expected_data = expected_data.replace("%ddb.path.project%", str(Path.cwd()))
            expected_data = expected_data.replace(
                "%network_name%", str(config.data.get("jsonnet.docker.compose.network_name"))
            )
            expected_data = expected_data.replace("%uid%", str(config.data.get("docker.user.uid")))
            expected_data = expected_data.replace("%gid%", str(config.data.get("docker.user.gid")))
            expected_data = expected_data.replace("%docker.debug.host%", str(config.data.get("docker.debug.host")))

            expected = yaml.load(expected_data, yaml.SafeLoader)

        assert rendered == expected

    @pytest.mark.parametrize(
        "variant",
        [
            "test-dev",
            "test-ci",
            "test-stage",
            "test-prod",
        ],
    )
    def test_docker_compose_traefik_no_https(self, project_loader, variant):
        def before_load_config():
            Path(f"ddb.{variant}.yml").rename("ddb.yml")
            Path(f"docker-compose.expected.{variant}.yml").rename("docker-compose.expected.yml")

        project_loader("docker_compose_traefik_no_https", before_load_config)

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(DockerFeature())
        features.register(JsonnetFeature())
        load_registered_features()
        register_actions_in_event_bus(fail_fast=True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert Path("docker-compose.yml").exists()
        with Path("docker-compose.yml").open() as f:
            rendered = yaml.load(f.read(), yaml.SafeLoader)

        with Path("docker-compose.expected.yml").open() as f:
            expected_data = f.read()

            if os.name == "nt":
                expected_data = expected_data.replace("%ddb.path.project%", path_as_posix_fast(str(Path.cwd())))
            else:
                expected_data = expected_data.replace("%ddb.path.project%", str(Path.cwd()))
            expected_data = expected_data.replace(
                "%network_name%", str(config.data.get("jsonnet.docker.compose.network_name"))
            )
            expected_data = expected_data.replace("%uid%", str(config.data.get("docker.user.uid")))
            expected_data = expected_data.replace("%gid%", str(config.data.get("docker.user.gid")))
            expected_data = expected_data.replace("%docker.debug.host%", str(config.data.get("docker.debug.host")))

            expected = yaml.load(expected_data, yaml.SafeLoader)

        assert rendered == expected

    @pytest.mark.parametrize(
        "variant",
        [
            "dev",
            "ci",
            "prod",
        ],
    )
    def test_docker_compose_traefik_defaults(self, project_loader, variant):
        def before_load_config():
            Path(f"ddb.{variant}.yml").rename("ddb.yml")
            Path(f"docker-compose.expected.{variant}.yml").rename("docker-compose.expected.yml")

        project_loader("docker_compose_traefik_defaults", before_load_config)

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(DockerFeature())
        features.register(JsonnetFeature())
        load_registered_features()
        register_actions_in_event_bus(fail_fast=True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert Path("docker-compose.yml").exists()
        with Path("docker-compose.yml").open() as f:
            rendered = yaml.load(f.read(), yaml.SafeLoader)

        with Path("docker-compose.expected.yml").open() as f:
            expected_data = f.read()

            if os.name == "nt":
                expected_data = expected_data.replace("%ddb.path.project%", path_as_posix_fast(str(Path.cwd())))
            else:
                expected_data = expected_data.replace("%ddb.path.project%", str(Path.cwd()))
            expected_data = expected_data.replace(
                "%network_name%", str(config.data.get("jsonnet.docker.compose.network_name"))
            )
            expected_data = expected_data.replace("%uid%", str(config.data.get("docker.user.uid")))
            expected_data = expected_data.replace("%gid%", str(config.data.get("docker.user.gid")))
            expected_data = expected_data.replace("%docker.debug.host%", str(config.data.get("docker.debug.host")))

            expected = yaml.load(expected_data, yaml.SafeLoader)

        assert rendered == expected

    def test_docker_compose_variables(self, project_loader):
        project_loader("docker_compose_variables")

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(DockerFeature())
        features.register(JsonnetFeature())
        load_registered_features()
        register_actions_in_event_bus(fail_fast=True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert Path("docker-compose.yml").exists()
        with Path("docker-compose.yml").open() as f:
            rendered = yaml.load(f.read(), yaml.SafeLoader)

        with Path("docker-compose.expected.yml").open() as f:
            expected_data = f.read()

            if os.name == "nt":
                expected_data = expected_data.replace("%ddb.path.project%", path_as_posix_fast(str(Path.cwd())))
            else:
                expected_data = expected_data.replace("%ddb.path.project%", str(Path.cwd()))
            expected_data = expected_data.replace(
                "%network_name%", str(config.data.get("jsonnet.docker.compose.network_name"))
            )
            expected_data = expected_data.replace("%uid%", str(config.data.get("docker.user.uid")))
            expected_data = expected_data.replace("%gid%", str(config.data.get("docker.user.gid")))
            expected_data = expected_data.replace("%docker.debug.host%", str(config.data.get("docker.debug.host")))

            expected = yaml.load(expected_data, yaml.SafeLoader)

        assert rendered == expected

    def test_docker_compose_project_dot_com(self, project_loader):
        project_loader("docker_compose_project_dot_com")

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(DockerFeature())
        features.register(JsonnetFeature())
        load_registered_features()
        register_actions_in_event_bus(fail_fast=True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert Path("docker-compose.yml").exists()
        with Path("docker-compose.yml").open() as f:
            rendered = yaml.load(f.read(), yaml.SafeLoader)

        with Path("docker-compose.expected.yml").open() as f:
            expected_data = f.read()

            if os.name == "nt":
                expected_data = expected_data.replace("%ddb.path.project%", path_as_posix_fast(str(Path.cwd())))
            else:
                expected_data = expected_data.replace("%ddb.path.project%", str(Path.cwd()))
            expected_data = expected_data.replace(
                "%network_name%", str(config.data.get("jsonnet.docker.compose.network_name"))
            )
            expected_data = expected_data.replace("%uid%", str(config.data.get("docker.user.uid")))
            expected_data = expected_data.replace("%gid%", str(config.data.get("docker.user.gid")))
            expected_data = expected_data.replace("%docker.debug.host%", str(config.data.get("docker.debug.host")))

            expected = yaml.load(expected_data, yaml.SafeLoader)

        assert rendered == expected

    def test_docker_compose_excluded_services(self, project_loader):
        project_loader("docker_compose_excluded_services")

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(DockerFeature())
        features.register(JsonnetFeature())
        load_registered_features()
        register_actions_in_event_bus(fail_fast=True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert Path("docker-compose.yml").exists()
        with Path("docker-compose.yml").open() as f:
            rendered = yaml.load(f.read(), yaml.SafeLoader)

        with Path("docker-compose.expected.yml").open() as f:
            expected_data = f.read()
            expected_data = expected_data.replace(
                "%network_name%", str(config.data.get("jsonnet.docker.compose.network_name"))
            )

            expected = yaml.load(expected_data, yaml.SafeLoader)

        assert rendered == expected

    def test_docker_compose_included_services(self, project_loader):
        project_loader("docker_compose_included_services")

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(DockerFeature())
        features.register(JsonnetFeature())
        load_registered_features()
        register_actions_in_event_bus(fail_fast=True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert Path("docker-compose.yml").exists()
        with Path("docker-compose.yml").open() as f:
            rendered = yaml.load(f.read(), yaml.SafeLoader)

        with Path("docker-compose.expected.yml").open() as f:
            expected_data = f.read()
            expected_data = expected_data.replace(
                "%network_name%", str(config.data.get("jsonnet.docker.compose.network_name"))
            )

            expected = yaml.load(expected_data, yaml.SafeLoader)

        assert rendered == expected

    @pytest.mark.parametrize(
        "variant",
        [
            "_register_binary",
            "_register_binary_with_one_option",
            # "_register_binary_with_multiple_options", TODO handle (options)(c1)
            "_shared_volumes",
            "_mount_volumes",
            "_mount_single_volume",
            "_mount_single_volume_with_default",
            "_expose",
        ],
    )
    def test_docker_compose_variants(self, project_loader, variant):
        project_loader("docker_compose" + variant)

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(DockerFeature())
        features.register(JsonnetFeature())
        load_registered_features()
        register_actions_in_event_bus(fail_fast=True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert Path("docker-compose.yml").exists()
        with Path("docker-compose.yml").open() as f:
            rendered = yaml.load(f.read(), yaml.SafeLoader)

        with Path("docker-compose.expected.yml").open() as f:
            expected_data = f.read()

            if os.name == "nt":
                expected_data = expected_data.replace("%ddb.path.project%", path_as_posix_fast(str(Path.cwd())))
            else:
                expected_data = expected_data.replace("%ddb.path.project%", str(Path.cwd()))
            expected_data = expected_data.replace(
                "%network_name%", str(config.data.get("jsonnet.docker.compose.network_name"))
            )
            expected_data = expected_data.replace("%uid%", str(config.data.get("docker.user.uid")))
            expected_data = expected_data.replace("%gid%", str(config.data.get("docker.user.gid")))
            expected_data = expected_data.replace("%docker.debug.host%", str(config.data.get("docker.debug.host")))

            expected = yaml.load(expected_data, yaml.SafeLoader)

        assert rendered == expected

        if variant == "_mount_single_volume":
            assert Path("volumes/shared-volume").is_dir()

        if variant == "_mount_single_volume_with_default":
            assert Path("shared-volume").is_dir()

    @pytest.mark.parametrize(
        "variant",
        [
            "default",
            "no_debug",
        ],
    )
    def test_docker_compose_xdebug(self, project_loader, variant):
        def before_load_config():
            Path(f"ddb.{variant}.yml").rename("ddb.yml")
            Path(f"docker-compose.expected.{variant}.yml").rename("docker-compose.expected.yml")

        project_loader("docker_compose_xdebug", before_load_config)

        print(Path.cwd())

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(DockerFeature())
        features.register(JsonnetFeature())
        load_registered_features()
        register_actions_in_event_bus(fail_fast=True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert Path("docker-compose.yml").exists()
        with Path("docker-compose.yml").open() as f:
            rendered = yaml.load(f.read(), yaml.SafeLoader)

        with Path("docker-compose.expected.yml").open() as f:
            expected_data = f.read()

            expected_data = expected_data.replace(
                "%network_name%", str(config.data.get("jsonnet.docker.compose.network_name"))
            )
            expected_data = expected_data.replace("%uid%", str(config.data.get("docker.user.uid")))
            expected_data = expected_data.replace("%gid%", str(config.data.get("docker.user.gid")))
            expected_data = expected_data.replace("%docker.debug.host%", str(config.data.get("docker.debug.host")))

            expected = yaml.load(expected_data, yaml.SafeLoader)

        assert rendered == expected


class TestJsonnetAutofix:
    def teardown_method(self, test_method):
        migrations.set_history()

    def test_autofix_variables_only(self, project_loader):
        project_loader("autofix_variables_only")

        config.args.autofix = True

        history = (
            PropertyMigration("old_property", "new_property", since="v1.1.0"),
            PropertyMigration("some.deep.old.property", "some.another.new.property", since="v1.1.0"),
        )

        migrations.set_history(history)

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(DockerFeature())
        features.register(JsonnetFeature())
        load_registered_features()
        register_actions_in_event_bus(fail_fast=True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert Path("variables.json").exists()
        with Path("variables.json").open() as f:
            rendered = f.read()

        with Path("variables.expected.json").open() as f:
            expected = f.read()

        assert expected == rendered

        with Path("variables.json.jsonnet").open() as f:
            source = f.read()

        with Path("variables.json.autofix").open() as f:
            fixed = f.read()

        assert source == fixed
