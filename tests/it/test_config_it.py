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
