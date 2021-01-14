import os
import pytest

from ddb.__main__ import main, reset
from ddb.config import config, Config
from tests.utilstest import setup_cfssl


class TestTraefik:
    @pytest.mark.docker
    def test_traefik_extra_services_with_remove(self, project_loader, module_scoped_container_getter):
        project_loader("extra-services")

        setup_cfssl(module_scoped_container_getter)

        main(["configure"])

        api_toml = os.path.join(config.paths.home, "traefik", "config", "sub.project.test.extra-service.api.toml")
        cert = os.path.join(config.paths.home, "certs", "sub.project.test.crt")
        key = os.path.join(config.paths.home, "certs", "sub.project.test.key")
        web_toml = os.path.join(config.paths.home, "traefik", "config", "rule.project.test.extra-service.web.toml")

        assert os.path.exists(api_toml)
        assert os.path.exists(cert)
        assert os.path.exists(key)
        assert os.path.exists(web_toml)

        with open("ddb.yml", "w"):
            pass

        Config.defaults = {'defaults': {'fail_fast': True}}

        setup_cfssl(module_scoped_container_getter)

        main(["configure"])

        assert not os.path.exists(api_toml)
        assert not os.path.exists(cert)
        assert not os.path.exists(key)
        assert not os.path.exists(web_toml)

    @pytest.mark.docker
    def test_traefik_extra_services_without_remove(self, project_loader, module_scoped_container_getter):
        project_loader("extra-services")

        setup_cfssl(module_scoped_container_getter)

        main(["configure"])

        api_toml = os.path.join(config.paths.home, "traefik", "config", "sub.project.test.extra-service.api.toml")
        cert = os.path.join(config.paths.home, "certs", "sub.project.test.crt")
        key = os.path.join(config.paths.home, "certs", "sub.project.test.key")
        web_toml = os.path.join(config.paths.home, "traefik", "config", "rule.project.test.extra-service.web.toml")

        assert os.path.exists(api_toml)
        assert os.path.exists(cert)
        assert os.path.exists(key)
        assert os.path.exists(web_toml)

        main(["configure"])

        assert os.path.exists(api_toml)
        assert os.path.exists(cert)
        assert os.path.exists(key)
        assert os.path.exists(web_toml)
