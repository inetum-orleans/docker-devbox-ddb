import os
from shutil import copy

from _pytest.capture import CaptureFixture
from ddb.__main__ import main
from ddb.config import Config


class TestBinaries:
    def test_docker_binaries(self, project_loader, capsys: CaptureFixture):
        project_loader("docker1")

        exceptions = main(["configure"])
        assert not exceptions

        exceptions = main(["run", "psql"])
        assert not exceptions

        output = capsys.readouterr()
        assert output.out.strip() == "docker-compose run --workdir=/workdir/. db psql"

    def test_docker_binaries_exe(self, project_loader, capsys: CaptureFixture):
        project_loader("docker1_exe")

        exceptions = main(["configure"])
        assert not exceptions

        exceptions = main(["run", "psql"])
        assert not exceptions

        output = capsys.readouterr()
        assert output.out.strip() == "docker-compose exec --workdir=/workdir/. db psql"

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
