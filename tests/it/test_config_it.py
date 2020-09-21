import os

from ddb.__main__ import main, reset
from ddb.config import config


class TestConfig:
    def test_config_override_shell(self, project_loader):
        project_loader("override-shell")

        os.environ['DDB_OVERRIDE_SHELL_SHELL'] = 'fish'

        main(["config"], reset_disabled=True)

        assert config.data.get('shell.shell') == 'fish'

        reset()

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
