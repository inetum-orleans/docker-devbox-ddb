import os
from shutil import copy

import pytest
from _pytest.capture import CaptureFixture

from ddb.__main__ import main, reset
from ddb.config import Config, config

docker_compose_bin = "docker-compose" if os.name != "nt" else "docker-compose.exe"


class TestBinaries:
    def test_docker_binaries(self, project_loader, capsys: CaptureFixture):
        project_loader("docker")

        exceptions = main(["configure"])
        assert not exceptions

        exceptions = main(["run", "psql"])
        assert not exceptions

        assert os.path.exists(os.path.join(os.getcwd(), '.bin', 'psql'))

        output = capsys.readouterr()
        assert output.out.strip() == docker_compose_bin + " run --rm --workdir=/workdir/. db psql"

    def test_docker_binaries_with_custom_options(self, project_loader, capsys: CaptureFixture):
        project_loader("docker")

        exceptions = main(["configure"])
        assert not exceptions

        os.environ['DDB_RUN_OPTS'] = "-e TEST"

        exceptions = main(["run", "psql"])
        assert not exceptions

        assert os.path.exists(os.path.join(os.getcwd(), '.bin', 'psql'))

        output = capsys.readouterr()
        assert output.out.strip() == docker_compose_bin + " run --rm --workdir=/workdir/. -e TEST db psql"

    def test_docker_binaries_exe(self, project_loader, capsys: CaptureFixture):
        project_loader("docker_exe")

        exceptions = main(["configure"])
        assert not exceptions

        exceptions = main(["run", "psql"])
        assert not exceptions

        assert os.path.exists(os.path.join(os.getcwd(), '.bin', 'psql'))

        output = capsys.readouterr()
        assert output.out.strip() == docker_compose_bin + " exec --workdir=/workdir/. db psql"

    def test_docker_binaries_entrypoint(self, project_loader, capsys: CaptureFixture):
        project_loader("docker_entrypoint")

        exceptions = main(["configure"])
        assert not exceptions

        exceptions = main(["run", "psql"])
        assert not exceptions

        assert os.path.exists(os.path.join(os.getcwd(), '.bin', 'psql'))

        output = capsys.readouterr()
        assert output.out.strip() == docker_compose_bin + " run --rm --workdir=/workdir/. --entrypoint=/custom/ep db psql"

    def test_docker_binaries_global(self, project_loader, capsys: CaptureFixture):
        project_loader("docker_global")

        exceptions = main(["configure"])
        assert not exceptions

        exceptions = main(["run", "psql"])
        assert not exceptions

        assert not os.path.exists(os.path.join(os.getcwd(), '.bin', 'psql'))
        assert os.path.exists(os.path.join(os.getcwd(), '..', 'home', '.bin', 'psql'))

        output = capsys.readouterr()
        assert output.out.strip() == docker_compose_bin + " run --rm --workdir=/workdir/. db psql"

    def test_docker_binaries_global_default(self, project_loader, capsys: CaptureFixture):
        project_loader("docker_global_default")

        exceptions = main(["configure"])
        assert not exceptions

        exceptions = main(["run", "psql"])
        assert not exceptions

        assert not os.path.exists(os.path.join(os.getcwd(), '.bin', 'psql'))
        assert os.path.exists(os.path.join(os.getcwd(), '..', 'home', '.bin', 'psql'))

        output = capsys.readouterr()
        assert output.out.strip() == docker_compose_bin + " run --rm --workdir=/workdir/. db psql"

    def test_docker_binaries_with_clear_cache(self, project_loader, capsys: CaptureFixture):
        project_loader("docker")

        main(["--clear-cache", "configure"])

        exceptions = main(["run", "psql"])
        assert not exceptions

        assert os.path.exists(os.path.join(os.getcwd(), '.bin', 'psql'))

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

        assert os.path.exists(os.path.join(os.getcwd(), '.bin', 'psql'))

        copy(os.path.join("..", "replacement", "docker-compose.yml.jsonnet"), 'docker-compose.yml.jsonnet')

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
    def test_docker_binaries_condition(self, relative_cwd, expected, project_loader, capsys: CaptureFixture):
        project_loader("docker_condition")

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
