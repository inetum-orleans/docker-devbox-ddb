from _pytest.capture import CaptureFixture

from ddb.__main__ import main


class TestBinaries:
    def test_docker_binaries(self, project_loader, capsys: CaptureFixture):
        project_loader("docker1")

        exceptions = main(["configure"])
        assert not exceptions

        exceptions = main(["run", "psql"])
        assert not exceptions

    def test_docker_binaries_with_clear_cache(self, project_loader, capsys: CaptureFixture):
        project_loader("docker1")

        main(["--clear-cache", "configure"])

        exceptions = main(["run", "psql"])
        assert not exceptions
