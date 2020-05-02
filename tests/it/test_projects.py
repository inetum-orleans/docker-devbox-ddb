import os

from ddb.__main__ import main


class TestSymfonyVuejs:
    def test_activate(self, project_loader):
        project_loader("symfony-vuejs")

        main(["configure"])

        main(["activate"])

        assert os.path.exists("docker-compose.override.yml")

        assert sorted(os.listdir(".docker/php/.ca-certificates")) == \
               sorted(("GFI_Informatique_Orléans_Root_CA.crt",
                       "some-cert.crt",
                       "fwca.annuaire.groupe.local.crt"))

        assert os.path.exists(os.path.join(".docker", "db", "Dockerfile"))
        assert os.path.exists(os.path.join(".docker", "php", "Dockerfile"))
        assert os.path.exists(os.path.join(".docker", "php", "fixuid.tar.gz"))
        with open(os.path.join(".docker", "php", "Dockerfile"), "r") as dockerfile:
            data = dockerfile.read()
            assert "COPY .ca-certificates/* /usr/local/share/ca-certificates/" in data
            assert "ADD fixuid.tar.gz /usr/local/bin" in data

        assert os.path.exists(".gitignore")
        with open(".gitignore", "r") as gitignore_file:
            gitignore_lines = gitignore_file.read().splitlines()
            assert gitignore_lines
