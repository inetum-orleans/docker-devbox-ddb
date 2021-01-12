import os
from shutil import copy

import pytest
from _pytest.capture import CaptureFixture

from ddb.__main__ import main, reset
from ddb.config import Config, config


docker_compose_bin = "docker-compose" if os.name != "nt" else "docker-compose.exe"

class TestBinaries:
    def test_docker_binaries(self, project_loader, capsys: CaptureFixture):
        project_loader("docker1")

        exceptions = main(["configure"])
        assert not exceptions

        exceptions = main(["run", "psql"])
        assert not exceptions

        output = capsys.readouterr()
        assert output.out.strip() == docker_compose_bin + " run --rm --workdir=/workdir/. db psql"

    def test_docker_binaries_exe(self, project_loader, capsys: CaptureFixture):
        project_loader("docker1_exe")

        exceptions = main(["configure"])
        assert not exceptions

        exceptions = main(["run", "psql"])
        assert not exceptions

        output = capsys.readouterr()
        assert output.out.strip() == docker_compose_bin + " exec --workdir=/workdir/. db psql"

    def test_docker_binaries_with_clear_cache(self, project_loader, capsys: CaptureFixture):
        project_loader("docker1")

        main(["--clear-cache", "configure"])

        exceptions = main(["run", "psql"])
        assert not exceptions

    def test_docker_binaries_removed(self, project_loader, capsys: CaptureFixture):
        Config.defaults = None

        project_loader("docker_removal")

        main(["configure"])

        if os.name == 'nt':
            assert os.path.isfile(os.path.join(".bin", "psql.bat"))
        else:
            assert os.path.isfile(os.path.join(".bin", "psql"))

        exceptions = main(["run", "psql"])
        assert not exceptions

        copy("docker-compose.removed.yml", 'docker-compose.yml')

        main(["configure"])

        assert not os.path.isfile(os.path.join(".bin", "psql"))

        exceptions = main(["run", "psql"])
        assert exceptions

        assert isinstance(exceptions[0], ValueError)
        assert str(exceptions[0]) == 'Binary name "psql" is not registered'

    @pytest.mark.parametrize(
        'relative_cwd,expected',
        [('node10', 'node10'), ('node12', 'node12'), (None, 'node14')]
    )
    def test_docker_binaries_with_condition(self, relative_cwd, expected, project_loader, capsys: CaptureFixture):
        project_loader("docker_command_cwd_condition")

        cwd = os.getcwd()
        if relative_cwd:
            cwd = os.path.join(cwd, relative_cwd)
            os.chdir(cwd)
            assert os.getcwd() == cwd

        try:
            main(["--clear-cache", "configure"], reset_disabled=True)
            assert config.cwd == cwd
        finally:
            reset()

        exceptions = main(["run", "node", "--version"])
        assert not exceptions

        outerr = capsys.readouterr()
        assert expected in outerr.out
