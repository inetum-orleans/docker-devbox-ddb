import zipfile
from pathlib import Path

from ddb.__main__ import main


class TestDjp:
    def test_djp(self, project_loader):
        project_loader("djp")

        with zipfile.ZipFile("template.zip", "r") as zip_ref:
            zip_ref.extractall("expected")

        main(["download"])

        assert Path(".docker/djp/Dockerfile.jinja").exists()
        assert Path(".docker/djp/djp.libjsonnet").exists()

        with Path(".docker/djp/djp.libjsonnet").open() as djp_libjsonnet:
            assert "// Edited\n" not in djp_libjsonnet.readlines()

    def test_djp_patch(self, project_loader):
        project_loader("djp_patch")

        main(["download"])

        assert Path(".docker/djp/Dockerfile.jinja").exists()
        assert Path(".docker/djp/djp.libjsonnet").exists()

        with Path(".docker/djp/Dockerfile.jinja").open() as djp_libjsonnet:
            assert "replaced" not in djp_libjsonnet.read()

        with Path(".docker/djp/djp.libjsonnet").open() as djp_libjsonnet:
            assert "// Edited\n" in djp_libjsonnet.readlines()
