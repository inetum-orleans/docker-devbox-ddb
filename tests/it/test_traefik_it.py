from pathlib import Path

import pytest

from ddb.__main__ import main
from ddb.config import Config, config
from tests.utilstest import setup_cfssl


class TestTraefik:
    @pytest.mark.docker
    def test_traefik_extra_services_with_remove(self, project_loader, module_scoped_container_getter):
        project_loader("extra-services")

        setup_cfssl(module_scoped_container_getter)

        main(["configure"])

        api_toml = str(Path(config.paths.home) / "traefik" / "config" / "sub.project.test.extra-service.api.toml")
        cert = str(Path(config.paths.home) / "certs" / "sub.project.test.crt")
        key = str(Path(config.paths.home) / "certs" / "sub.project.test.key")
        web_toml = str(Path(config.paths.home) / "traefik" / "config" / "rule.project.test.extra-service.web.toml")

        assert Path(api_toml).exists()
        assert Path(cert).exists()
        assert Path(key).exists()
        assert Path(web_toml).exists()

        with Path("ddb.yml").open("w"):
            pass

        Config.defaults = {"defaults": {"fail_fast": True}}

        setup_cfssl(module_scoped_container_getter)

        main(["configure"])

        assert not Path(api_toml).exists()
        assert not Path(cert).exists()
        assert not Path(key).exists()
        assert not Path(web_toml).exists()

    @pytest.mark.docker
    def test_traefik_extra_services_without_remove(self, project_loader, module_scoped_container_getter):
        project_loader("extra-services")

        setup_cfssl(module_scoped_container_getter)

        main(["configure"])

        api_toml = str(Path(config.paths.home) / "traefik" / "config" / "sub.project.test.extra-service.api.toml")
        cert = str(Path(config.paths.home) / "certs" / "sub.project.test.crt")
        key = str(Path(config.paths.home) / "certs" / "sub.project.test.key")
        web_toml = str(Path(config.paths.home) / "traefik" / "config" / "rule.project.test.extra-service.web.toml")

        assert Path(api_toml).exists()
        assert Path(cert).exists()
        assert Path(key).exists()
        assert Path(web_toml).exists()

        main(["configure"])

        assert Path(api_toml).exists()
        assert Path(cert).exists()
        assert Path(key).exists()
        assert Path(web_toml).exists()
