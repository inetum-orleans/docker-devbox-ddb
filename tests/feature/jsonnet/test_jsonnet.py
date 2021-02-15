import os
import re

import pathlib
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


class TestJsonnetAction:
    def test_empty_project_without_core(self, project_loader):
        project_loader("empty")

        features.register(FileFeature())
        features.register(JsonnetFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

    def test_empty_project_with_core(self, project_loader):
        project_loader("empty")

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(JsonnetFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

    @pytest.mark.skipif("os.name == 'nt'")
    def test_named_user_group(self, project_loader):
        project_loader("empty")

        features.register(JsonnetFeature())
        load_registered_features()

        assert config.data.get('jsonnet.docker.user.name_to_uid')
        assert config.data.get('jsonnet.docker.user.group_to_gid')

    @pytest.mark.skipif("os.name != 'nt'")
    def test_named_user_group_windows(self, project_loader):
        project_loader("empty")

        features.register(JsonnetFeature())
        load_registered_features()

        assert config.data.get('jsonnet.docker.user.name_to_uid') == {}
        assert config.data.get('jsonnet.docker.user.group_to_gid') == {}

    def test_example1(self, project_loader):
        project_loader("example1")

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(JsonnetFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert os.path.exists('example1.json')
        with open('example1.json', 'r') as f:
            example = f.read()

        with open('example1.expected.json', 'r') as f:
            example_expected = f.read()

        assert example == example_expected

    def test_example1_yaml(self, project_loader):
        project_loader("example1.yaml")

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(JsonnetFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert os.path.exists('example1.another')
        with open('example1.another', 'r') as f:
            example_another = f.read()

        with open('example1.expected.another', 'r') as f:
            example_another_expected = f.read()

        assert example_another == example_another_expected

        assert os.path.exists('example1.yaml')
        with open('example1.yaml', 'r') as f:
            example_yaml = f.read()

        with open('example1.expected.yaml', 'r') as f:
            example_yaml_expected = f.read()

        assert example_yaml == example_yaml_expected

    def test_example2(self, project_loader):
        project_loader("example2")

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(JsonnetFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert os.path.exists('example2.json')
        with open('example2.json', 'r') as f:
            example = f.read()

        with open('example2.expected.json', 'r') as f:
            example_expected = f.read()

        assert example == example_expected

    def test_example3(self, project_loader):
        project_loader("example3")

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(JsonnetFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert os.path.exists('uwsgi.ini')
        with open('uwsgi.ini', 'r') as f:
            iwsgi = f.read()

        with open('uwsgi.expected.ini', 'r') as f:
            iwsgi_expected = f.read()

        assert iwsgi == iwsgi_expected

        assert os.path.exists('init.sh')
        with open('init.sh', 'r') as f:
            init = f.read()

        with open('init.expected.sh', 'r') as f:
            init_expected = f.read()

        assert init == init_expected

        assert os.path.exists('cassandra.conf')
        with open('cassandra.conf', 'r') as f:
            cassandra = f.read()

        with open('cassandra.expected.conf', 'r') as f:
            cassandra_expected = f.read()

        assert cassandra == cassandra_expected

    def test_example3_with_dir(self, project_loader):
        project_loader("example3.with_dir")

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(JsonnetFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert os.path.exists('./target/uwsgi.ini')
        with open('./target/uwsgi.ini', 'r') as f:
            iwsgi = f.read()

        with open('uwsgi.expected.ini', 'r') as f:
            iwsgi_expected = f.read()

        assert iwsgi == iwsgi_expected

        assert os.path.exists('./target/init.sh')
        with open('./target/init.sh', 'r') as f:
            init = f.read()

        with open('init.expected.sh', 'r') as f:
            init_expected = f.read()

        assert init == init_expected

        assert os.path.exists('./target/cassandra.conf')
        with open('./target/cassandra.conf', 'r') as f:
            cassandra = f.read()

        with open('cassandra.expected.conf', 'r') as f:
            cassandra_expected = f.read()

        assert cassandra == cassandra_expected

    def test_config_variables(self, project_loader):
        project_loader("config_variables")

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(JsonnetFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert os.path.exists('variables.json')
        with open('variables.json', 'r') as f:
            variables = f.read()

        with open('variables.expected.json', 'r') as f:
            variables_expected = f.read()

        assert variables == variables_expected

    @pytest.mark.parametrize("variant", [
        "test-dev",
        "test-ci",
        "test-stage",
        "test-prod",
    ])
    def test_docker_compose_traefik(self, project_loader, variant):
        def before_load_config():
            os.rename("ddb.%s.yml" % variant, "ddb.yml")
            os.rename("docker-compose.expected.%s.yml" % variant, "docker-compose.expected.yml")

        project_loader("docker_compose_traefik", before_load_config)

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(DockerFeature())
        features.register(JsonnetFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert os.path.exists('docker-compose.yml')
        with open('docker-compose.yml', 'r') as f:
            rendered = yaml.load(f.read(), yaml.SafeLoader)

        with open('docker-compose.expected.yml', 'r') as f:
            expected_data = f.read()

            if os.name == 'nt':
                mapped_cwd = re.sub(r"^([a-zA-Z]):", r"/\1", os.getcwd())
                mapped_cwd = pathlib.Path(mapped_cwd).as_posix()

                expected_data = expected_data.replace("%ddb.path.project%", mapped_cwd)
            else:
                expected_data = expected_data.replace("%ddb.path.project%", os.getcwd())
            expected_data = expected_data.replace("%uid%", str(config.data.get('docker.user.uid')))
            expected_data = expected_data.replace("%gid%", str(config.data.get('docker.user.gid')))
            expected_data = expected_data.replace("%docker.debug.host%", str(config.data.get('docker.debug.host')))

            expected = yaml.load(expected_data, yaml.SafeLoader)

        assert rendered == expected

    @pytest.mark.parametrize("variant", [
        "test-dev",
        "test-ci",
        "test-stage",
        "test-prod",
    ])
    def test_docker_compose_traefik_no_https(self, project_loader, variant):
        def before_load_config():
            os.rename("ddb.%s.yml" % variant, "ddb.yml")
            os.rename("docker-compose.expected.%s.yml" % variant, "docker-compose.expected.yml")

        project_loader("docker_compose_traefik_no_https", before_load_config)

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(DockerFeature())
        features.register(JsonnetFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert os.path.exists('docker-compose.yml')
        with open('docker-compose.yml', 'r') as f:
            rendered = yaml.load(f.read(), yaml.SafeLoader)

        with open('docker-compose.expected.yml', 'r') as f:
            expected_data = f.read()

            if os.name == 'nt':
                mapped_cwd = re.sub(r"^([a-zA-Z]):", r"/\1", os.getcwd())
                mapped_cwd = pathlib.Path(mapped_cwd).as_posix()

                expected_data = expected_data.replace("%ddb.path.project%", mapped_cwd)
            else:
                expected_data = expected_data.replace("%ddb.path.project%", os.getcwd())
            expected_data = expected_data.replace("%uid%", str(config.data.get('docker.user.uid')))
            expected_data = expected_data.replace("%gid%", str(config.data.get('docker.user.gid')))
            expected_data = expected_data.replace("%docker.debug.host%", str(config.data.get('docker.debug.host')))

            expected = yaml.load(expected_data, yaml.SafeLoader)

        assert rendered == expected

    @pytest.mark.parametrize("variant", [
        "dev",
        "ci",
        "prod",
    ])
    def test_docker_compose_traefik_defaults(self, project_loader, variant):
        def before_load_config():
            os.rename("ddb.%s.yml" % variant, "ddb.yml")
            os.rename("docker-compose.expected.%s.yml" % variant, "docker-compose.expected.yml")

        project_loader("docker_compose_traefik_defaults", before_load_config)

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(DockerFeature())
        features.register(JsonnetFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert os.path.exists('docker-compose.yml')
        with open('docker-compose.yml', 'r') as f:
            rendered = yaml.load(f.read(), yaml.SafeLoader)

        with open('docker-compose.expected.yml', 'r') as f:
            expected_data = f.read()

            if os.name == 'nt':
                mapped_cwd = re.sub(r"^([a-zA-Z]):", r"/\1", os.getcwd())
                mapped_cwd = pathlib.Path(mapped_cwd).as_posix()

                expected_data = expected_data.replace("%ddb.path.project%", mapped_cwd)
            else:
                expected_data = expected_data.replace("%ddb.path.project%", os.getcwd())
            expected_data = expected_data.replace("%uid%", str(config.data.get('docker.user.uid')))
            expected_data = expected_data.replace("%gid%", str(config.data.get('docker.user.gid')))
            expected_data = expected_data.replace("%docker.debug.host%", str(config.data.get('docker.debug.host')))

            expected = yaml.load(expected_data, yaml.SafeLoader)

        assert rendered == expected

    def test_docker_compose_variables(self, project_loader):
        project_loader("docker_compose_variables")

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(DockerFeature())
        features.register(JsonnetFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert os.path.exists('docker-compose.yml')
        with open('docker-compose.yml', 'r') as f:
            rendered = yaml.load(f.read(), yaml.SafeLoader)

        with open('docker-compose.expected.yml', 'r') as f:
            expected_data = f.read()

            if os.name == 'nt':
                mapped_cwd = re.sub(r"^([a-zA-Z]):", r"/\1", os.getcwd())
                mapped_cwd = pathlib.Path(mapped_cwd).as_posix()

                expected_data = expected_data.replace("%ddb.path.project%", mapped_cwd)
            else:
                expected_data = expected_data.replace("%ddb.path.project%", os.getcwd())
            expected_data = expected_data.replace("%uid%", str(config.data.get('docker.user.uid')))
            expected_data = expected_data.replace("%gid%", str(config.data.get('docker.user.gid')))
            expected_data = expected_data.replace("%docker.debug.host%", str(config.data.get('docker.debug.host')))

            expected = yaml.load(expected_data, yaml.SafeLoader)

        assert rendered == expected

    def test_docker_compose_excluded_services(self, project_loader):
        project_loader("docker_compose_excluded_services")

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(DockerFeature())
        features.register(JsonnetFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert os.path.exists('docker-compose.yml')
        with open('docker-compose.yml', 'r') as f:
            rendered = yaml.load(f.read(), yaml.SafeLoader)

        with open('docker-compose.expected.yml', 'r') as f:
            expected_data = f.read()
            expected = yaml.load(expected_data, yaml.SafeLoader)

        assert rendered == expected

    def test_docker_compose_included_services(self, project_loader):
        project_loader("docker_compose_included_services")

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(DockerFeature())
        features.register(JsonnetFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert os.path.exists('docker-compose.yml')
        with open('docker-compose.yml', 'r') as f:
            rendered = yaml.load(f.read(), yaml.SafeLoader)

        with open('docker-compose.expected.yml', 'r') as f:
            expected_data = f.read()
            expected = yaml.load(expected_data, yaml.SafeLoader)

        assert rendered == expected

    @pytest.mark.parametrize("variant", [
        "_register_binary",
        "_register_binary_with_one_option",
        # "_register_binary_with_multiple_options", TODO handle (options)(c1)
        "_shared_volumes",
        "_mount_volumes",
        "_mount_single_volume",
        "_mount_single_volume_with_default",
        "_expose"
    ])
    def test_docker_compose_variants(self, project_loader, variant):
        project_loader("docker_compose" + variant)

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(DockerFeature())
        features.register(JsonnetFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert os.path.exists('docker-compose.yml')
        with open('docker-compose.yml', 'r') as f:
            rendered = yaml.load(f.read(), yaml.SafeLoader)

        with open('docker-compose.expected.yml', 'r') as f:
            expected_data = f.read()

            if os.name == 'nt':
                mapped_cwd = re.sub(r"^([a-zA-Z]):", r"/\1", os.getcwd())
                mapped_cwd = pathlib.Path(mapped_cwd).as_posix()

                expected_data = expected_data.replace("%ddb.path.project%", mapped_cwd)
            else:
                expected_data = expected_data.replace("%ddb.path.project%", os.getcwd())
            expected_data = expected_data.replace("%uid%", str(config.data.get('docker.user.uid')))
            expected_data = expected_data.replace("%gid%", str(config.data.get('docker.user.gid')))
            expected_data = expected_data.replace("%docker.debug.host%", str(config.data.get('docker.debug.host')))

            expected = yaml.load(expected_data, yaml.SafeLoader)

        assert rendered == expected

        if variant == '_mount_single_volume':
            assert os.path.isdir('volumes/shared-volume')

        if variant == '_mount_single_volume_with_default':
            assert os.path.isdir('shared-volume')

    @pytest.mark.parametrize("variant", [
        "default",
        "no_debug",
    ])
    def test_docker_compose_xdebug(self, project_loader, variant):
        def before_load_config():
            os.rename("ddb.%s.yml" % variant, "ddb.yml")
            os.rename("docker-compose.expected.%s.yml" % variant, "docker-compose.expected.yml")

        project_loader("docker_compose_xdebug", before_load_config)

        print(os.getcwd())

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(DockerFeature())
        features.register(JsonnetFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert os.path.exists('docker-compose.yml')
        with open('docker-compose.yml', 'r') as f:
            rendered = yaml.load(f.read(), yaml.SafeLoader)

        with open('docker-compose.expected.yml', 'r') as f:
            expected_data = f.read()

            expected_data = expected_data.replace("%uid%", str(config.data.get('docker.user.uid')))
            expected_data = expected_data.replace("%gid%", str(config.data.get('docker.user.gid')))
            expected_data = expected_data.replace("%docker.debug.host%", str(config.data.get('docker.debug.host')))

            expected = yaml.load(expected_data, yaml.SafeLoader)

        assert rendered == expected


class TestJsonnetAutofix:
    def teardown_method(self, test_method):
        migrations.set_history()

    def test_autofix_variables_only(self, project_loader):
        project_loader("autofix_variables_only")

        config.args.autofix = True

        history = (
            PropertyMigration("old_property",
                              "new_property", since="v1.1.0"),
            PropertyMigration("some.deep.old.property",
                              "some.another.new.property", since="v1.1.0"),
        )

        migrations.set_history(history)

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(DockerFeature())
        features.register(JsonnetFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert os.path.exists('variables.json')
        with open('variables.json', 'r') as f:
            rendered = f.read()

        with open('variables.expected.json', 'r') as f:
            expected = f.read()

        assert expected == rendered

        with open('variables.json.jsonnet', 'r') as f:
            source = f.read()

        with open('variables.json.autofix', 'r') as f:
            fixed = f.read()

        assert source == fixed
