import os
from pathlib import Path
from shutil import copy

import pytest
from _pytest.capture import CaptureFixture

from ddb.__main__ import main, reset
from ddb.config import Config, config
from tests.utilstest import local_path

docker_compose_bin = "docker compose" if os.name != "nt" else "docker.exe compose"
bin_ext = ".bat" if os.name == "nt" else ""


class TestBinaries:
    def test_docker_binaries(self, project_loader, capsys: CaptureFixture):
        project_loader("docker")

        exceptions = main(["configure"])
        assert not exceptions

        exceptions = main(["run", "psql"])
        assert not exceptions

        assert (Path.cwd() / ".bin" / ("psql" + bin_ext)).exists()

        output = capsys.readouterr()
        assert (
            output.out.strip()
            == docker_compose_bin + f" -f {local_path('.', 'docker-compose.yml')} run --rm --workdir=/workdir/. db psql"
        )

    def test_docker_binaries_with_custom_options(self, project_loader, capsys: CaptureFixture):
        project_loader("docker")

        exceptions = main(["configure"])
        assert not exceptions

        os.environ["DDB_RUN_OPTS"] = "-e TEST"

        exceptions = main(["run", "psql"])
        assert not exceptions

        assert (Path.cwd() / ".bin" / ("psql" + bin_ext)).exists()

        output = capsys.readouterr()

        assert (
            output.out.strip()
            == docker_compose_bin
            + f" -f {local_path('.', 'docker-compose.yml')} run --rm --workdir=/workdir/. -e TEST db psql"
        )

    @pytest.mark.docker
    def test_docker_binaries_exe(self, project_loader, capsys: CaptureFixture):
        project_loader("docker_exe")

        exceptions = main(["configure"])
        assert not exceptions

        exceptions = main(["run", "psql"])
        assert not exceptions

        assert (Path.cwd() / ".bin" / ("psql" + bin_ext)).exists()

        output = capsys.readouterr()
        assert output.out.strip() == docker_compose_bin + " exec --workdir=/workdir/. db psql"

    def test_docker_binaries_entrypoint(self, project_loader, capsys: CaptureFixture):
        project_loader("docker_entrypoint")

        exceptions = main(["configure"])
        assert not exceptions

        exceptions = main(["run", "psql"])
        assert not exceptions

        assert (Path.cwd() / ".bin" / ("psql" + bin_ext)).exists()

        output = capsys.readouterr()
        assert (
            output.out.strip()
            == docker_compose_bin
            + f" -f {local_path('.', 'docker-compose.yml')} run --rm --workdir=/workdir/. --entrypoint=/custom/ep db psql"
        )

    def test_docker_binaries_global(self, project_loader, capsys: CaptureFixture):
        project_loader("docker_global")

        exceptions = main(["configure"])
        assert not exceptions

        exceptions = main(["run", "psql"])
        assert not exceptions

        assert not (Path.cwd() / ".bin" / ("psql" + bin_ext)).exists()
        assert (Path.cwd() / ".." / "home" / ".bin" / ("psql" + bin_ext)).exists()

        output = capsys.readouterr()
        assert (
            output.out.strip()
            == docker_compose_bin + f" -f {local_path('.', 'docker-compose.yml')} run --rm --workdir=/workdir/. db psql"
        )

    def test_docker_binaries_global_default(self, project_loader, capsys: CaptureFixture):
        project_loader("docker_global_default")

        exceptions = main(["configure"])
        assert not exceptions

        exceptions = main(["run", "psql"])
        assert not exceptions

        assert not (Path.cwd() / ".bin" / ("psql" + bin_ext)).exists()
        assert (Path.cwd() / ".." / "home" / ".bin" / ("psql" + bin_ext)).exists()

        output = capsys.readouterr()
        assert (
            output.out.strip()
            == docker_compose_bin + f" -f {local_path('.', 'docker-compose.yml')} run --rm --workdir=/workdir/. db psql"
        )

    def test_docker_binaries_with_clear_cache(self, project_loader, capsys: CaptureFixture):
        project_loader("docker")

        main(["--clear-cache", "configure"])

        exceptions = main(["run", "psql"])
        assert not exceptions

        assert (Path.cwd() / ".bin" / ("psql" + bin_ext)).exists()

    def test_docker_binaries_removed(self, project_loader, capsys: CaptureFixture):
        Config.defaults = None

        project_loader("docker_removal")

        main(["configure"])

        assert (Path(".bin") / ("psql" + bin_ext)).is_file()

        exceptions = main(["run", "psql"])
        assert not exceptions

        assert (Path.cwd() / ".bin" / ("psql" + bin_ext)).exists()

        copy(str(Path("..") / "replacement" / "docker-compose.yml.jsonnet"), "docker-compose.yml.jsonnet")

        main(["configure"])

        assert not (Path(".bin") / ("psql" + bin_ext)).is_file()

        exceptions = main(["run", "psql"])
        assert exceptions

        assert isinstance(exceptions[0], ValueError)
        assert str(exceptions[0]) == 'Binary name "psql" is not registered'

    @pytest.mark.parametrize(
        ("relative_cwd", "expected"), [("node10", "node10"), ("node12", "node12"), (None, "node14")]
    )
    def test_docker_binaries_condition(self, relative_cwd, expected, project_loader, capsys: CaptureFixture):
        project_loader("docker_condition")

        cwd = str(Path.cwd())
        if relative_cwd:
            cwd = str(Path(cwd) / relative_cwd)
            os.chdir(cwd)
            assert str(Path.cwd()) == cwd

        try:
            main(["--clear-cache", "configure"], reset_disabled=True)
            assert config.cwd == cwd
        finally:
            reset()

        exceptions = main(["run", "node", "--version"])
        assert not exceptions

        outerr = capsys.readouterr()
        assert expected in outerr.out
