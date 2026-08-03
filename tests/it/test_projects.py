from pathlib import Path

from ddb.__main__ import main


class TestSymfonyVuejs:
    def test_activate(self, project_loader):
        project_loader("symfony-vuejs")

        main(["activate"])

        main(["configure"])

        assert Path("docker-compose.override.yml").exists()

        assert sorted(path.name for path in Path(".docker/php/.ca-certificates").iterdir()) == sorted(
            ("GFI_Informatique_Orléans_Root_CA.crt", "some-cert.crt", "fwca.annuaire.groupe.local.crt")
        )

        assert (Path(".docker") / "db" / "Dockerfile").exists()
        assert (Path(".docker") / "php" / "Dockerfile").exists()
        assert (Path(".docker") / "php" / "fixuid.tar.gz").exists()
        with (Path(".docker") / "php" / "Dockerfile").open() as dockerfile:
            data = dockerfile.read()
            assert "COPY .ca-certificates/* /usr/local/share/ca-certificates/" in data
            assert "ADD fixuid.tar.gz /usr/local/bin" in data

        assert Path(".gitignore").exists()
        with Path(".gitignore").open() as gitignore_file:
            gitignore_lines = gitignore_file.read().splitlines()
            assert gitignore_lines
