import os

from ddb.__main__ import main
from ddb.config import config
from tests.utilstest import setup_cfssl


class TestTraefik:
    def test_traefik_extra_services(self, project_loader, module_scoped_container_getter):
        project_loader("extra-services")

        setup_cfssl(module_scoped_container_getter)

        main(["configure"])

        api_toml = os.path.join(config.paths.home, "traefik", "config", "sub.project.test.extra-service.api.toml")
        assert os.path.exists(api_toml)

        cert = os.path.join(config.paths.home, "certs", "sub.project.test.crt")
        assert os.path.exists(cert)

        key = os.path.join(config.paths.home, "certs", "sub.project.test.key")
        assert os.path.exists(key)

        web_toml = os.path.join(config.paths.home, "traefik", "config", "rule.project.test.extra-service.web.toml")
        assert os.path.exists(web_toml)
