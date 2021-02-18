import os

import yaml
from _pytest.capture import CaptureFixture
from dotty_dict import Dotty

from ddb.__main__ import main, reset
from ddb.config import config


class TestConfig:
    def test_config_override_shell(self, project_loader):
        project_loader("override-shell")

        os.environ['DDB_OVERRIDE_SHELL_SHELL'] = 'fish'

        main(["config"], reset_disabled=True)

        assert config.data.get('shell.shell') == 'fish'

        reset()

    def test_config_override_ci(self, project_loader):
        project_loader("override-ci")

        os.chdir("sub")

        main(["config"], reset_disabled=True)

        assert config.data.get('core.env.current') == 'ci'
        assert config.data.get('docker.cache_from_image') is True
        assert config.data.get('docker.registry.name') == "gfiorleans.azurecr.io"
        assert config.data.get('docker.registry.repository') == "alm-atout"

        reset()

    def test_config_output_extra_filenames(self, project_loader, capsys: CaptureFixture):
        project_loader("extra-filenames")

        main(["config"])

        configuration = Dotty(yaml.safe_load(capsys.readouterr().out))

        assert configuration['app.value'] == 'local'
        assert configuration['some'] is True
        assert configuration['another'] is True
        assert configuration['core.configuration.extra'] == ['some.custom.yml', 'another.config.file']

        reset()

    def test_config_output_extra_filenames_files_option(self, project_loader, capsys: CaptureFixture):
        project_loader("extra-filenames")

        main(["config", "--files"])

        reset()

        output = capsys.readouterr().out

        parts = [part.lstrip() for part in output.split('---') if part.strip()]
        assert len(parts) == 4

        configurations = {}

        for part in parts:
            filename, config = part.split('\n', 1)
            assert filename.startswith('# ')
            filename = filename[2:]
            filename = os.path.relpath(filename, os.getcwd())
            configurations[filename] = Dotty(yaml.safe_load(config))

        assert ('ddb.yml', 'some.custom.yml', 'another.config.file.yaml', 'ddb.local.yml') == \
               tuple(configurations.keys())

        assert configurations['ddb.yml']['app.value'] == 'default'
        assert configurations['some.custom.yml']['app.value'] == 'custom'
        assert configurations['another.config.file.yaml']['app.value'] == 'config'
        assert configurations['ddb.local.yml']['app.value'] == 'local'

    def test_config_output_extra_filenames_some_files_option(self, project_loader, capsys: CaptureFixture):
        project_loader("extra-filenames")

        main(["config", "some", "--files"])

        reset()

        output = capsys.readouterr().out

        parts = [part.lstrip() for part in output.split('---') if part.strip()]
        assert len(parts) == 1

        configurations = {}

        for part in parts:
            filename, config = part.split('\n', 1)
            assert filename.startswith('# ')
            filename = filename[2:]
            filename = os.path.relpath(filename, os.getcwd())
            configurations[filename] = Dotty(yaml.safe_load(config))

        assert ('some.custom.yml',) == \
               tuple(configurations.keys())

        assert configurations['some.custom.yml']['some'] is True
        assert 'app.value' not in configurations['some.custom.yml']

    def test_config_local_falsy(self, project_loader):
        project_loader("local-falsy")

        main(["configure"], reset_disabled=True)

        assert config.data.get('app.disabled_services') == []

        reset()

    def test_config_custom_strategy(self, project_loader):
        project_loader("local-custom-strategy")

        main(["configure"], reset_disabled=True)

        assert config.data.get('app.disabled_services') == ['python', 'gunicorn', 'another']
        assert config.data.get('app.another_strategy') == ['another', 'python', 'gunicorn']

        reset()

    def test_config_deep_custom_strategy(self, project_loader):
        project_loader("deep-local-custom-strategy")

        main(["configure"], reset_disabled=True)

        assert config.data.get('app.deep.disabled_services') == ['python', 'gunicorn', 'another']
        assert config.data.get('app.deep.another_strategy') == ['another', 'python', 'gunicorn']

        reset()

    def test_config_env_ddb(self, project_loader):
        project_loader("env-ddb")

        main(["configure"], reset_disabled=True)

        assert not config.data.get('app.test')

        reset()

    def test_config_env_ddb2(self, project_loader):
        project_loader("env-ddb")

        os.rename('ddb.dev.tmp.yml', 'ddb.dev.yml')

        main(["configure"], reset_disabled=True)

        assert config.data.get('app.test')
        assert not os.path.islink("ddb.yml")

        reset()

    def test_config_extra_filenames(self, project_loader):
        project_loader("extra-filenames")

        main(["configure"], reset_disabled=True)

        assert config.data.get('another') is True
        assert config.data.get('some') is True
        assert config.data.get('app.value') == 'local'

        reset()

    def test_config_merge_default(self, project_loader):
        project_loader("merge-default")

        main(["configure"], reset_disabled=True)

        assert config.data.get('core.env.current') == 'dev-services'
        assert config.data.get('core.env.available') == ['prod', 'stage', 'ci', 'dev', 'dev-services']

        reset()

    def test_config_merge_insert_strategy(self, project_loader):
        project_loader("merge-insert-strategy")

        main(["configure"], reset_disabled=True)

        assert config.data.get('core.env.current') == 'dev'
        assert config.data.get('core.env.available') == ['prod', 'stage', 'ci', 'dev-services', 'dev-services2', 'dev']

        reset()

    def test_config_merge_insert_strategy2(self, project_loader):
        project_loader("merge-insert-strategy2")

        main(["configure"], reset_disabled=True)

        assert config.data.get('core.env.current') == 'dev'
        assert config.data.get('core.env.available') == ['prod', 'prod-services', 'prod-services2', 'stage', 'ci',
                                                         'dev']

        reset()

    def test_config_merge_insert_strategy3(self, project_loader):
        project_loader("merge-insert-strategy3")

        main(["configure"], reset_disabled=True)

        assert config.data.get('core.env.current') == 'dev'
        assert config.data.get('core.env.available') == ['prod', 'prod', 'stage', 'stage', 'ci',
                                                         'dev']

        reset()

    def test_config_more_properties_jsonnet_docker(self, project_loader, capsys: CaptureFixture):
        project_loader("more-properties")

        main(["config", "jsonnet.docker"])

        configuration = Dotty(yaml.safe_load(capsys.readouterr().out))

        assert configuration['jsonnet.docker.compose.project_name'] == 'yo-custom'
        assert configuration['jsonnet.docker.registry.name'] == 'gfiorleans.azurecr.io'
        assert configuration['jsonnet.docker.registry.repository'] == 'yo-custom'
        assert configuration['jsonnet.docker.virtualhost.redirect_to_https'] is True

        assert 'docker' not in configuration
        assert 'core' not in configuration

        reset()

    def test_config_more_properties_jsonnet_docker_compose(self, project_loader, capsys: CaptureFixture):
        project_loader("more-properties")

        main(["config", "jsonnet.docker.compose"])

        configuration = Dotty(yaml.safe_load(capsys.readouterr().out))

        assert configuration['jsonnet.docker.compose.project_name'] == 'yo-custom'
        assert 'jsonnet.docker.registry.name' not in configuration
        assert 'jsonnet.docker.registry.repository' not in configuration
        assert 'jsonnet.docker.virtualhost.redirect_to_https' not in configuration
        assert 'docker' not in configuration
        assert 'core' not in configuration

        reset()

    def test_config_more_properties_docker_variables_full(self, project_loader, capsys: CaptureFixture):
        project_loader("more-properties")

        main(["config", "docker", "--variables", "--full"], reset_disabled=True)

        out = capsys.readouterr().out

        docker_ip = config.data.get('docker.ip')
        docker_interface = config.data.get('docker.interface')
        docker_user_gid = config.data.get('docker.user.gid')
        docker_user_uid = config.data.get('docker.user.uid')

        assert out == f"""docker.disabled: False
docker.interface: {docker_interface}
docker.ip: {docker_ip}
docker.user.gid: {docker_user_gid}
docker.user.group: None
docker.user.name: None
docker.user.uid: {docker_user_uid}
"""

        reset()

    def test_config_more_properties_docker_user_variables(self, project_loader, capsys: CaptureFixture):
        project_loader("more-properties")

        main(["config", "docker.user", "--variables"], reset_disabled=True)

        out = capsys.readouterr().out

        docker_user_gid = config.data.get('docker.user.gid')
        docker_user_uid = config.data.get('docker.user.uid')

        assert out == f"""docker.user.gid: {docker_user_gid}
docker.user.group: None
docker.user.name: None
docker.user.uid: {docker_user_uid}
"""

        reset()

    def test_config_more_properties_docker_ip_value(self, project_loader, capsys: CaptureFixture):
        project_loader("more-properties")

        main(["config", "docker.ip", "--value"], reset_disabled=True)

        out = capsys.readouterr().out

        docker_ip = config.data.get('docker.ip')

        assert out == f"{docker_ip}\n"

        reset()

    def test_config_more_properties_core_env_available_value(self, project_loader, capsys: CaptureFixture):
        project_loader("more-properties")

        main(["config", "core.env.available", "--value"], reset_disabled=True)

        out = capsys.readouterr().out

        available = config.data.get('core.env.available')

        assert out == f"{available}\n"

        reset()
