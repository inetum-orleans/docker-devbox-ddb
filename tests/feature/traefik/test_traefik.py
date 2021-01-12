import os
from pathlib import Path

from ddb.__main__ import load_registered_features
from ddb.config import config
from ddb.feature import features
from ddb.feature.core import CoreFeature
from ddb.feature.docker import DockerFeature
from ddb.feature.jsonnet import JsonnetFeature
from ddb.feature.traefik import TraefikFeature
from ddb.feature.traefik.actions import TraefikInstalllCertsAction, TraefikUninstalllCertsAction, \
    TraefikExtraServicesAction


class TestTraefikFeature:
    def test_empty_project_without_core(self, project_loader):
        project_loader("empty")

        features.register(TraefikFeature())
        load_registered_features()

        assert config.data.get('traefik.disabled') is True

    def test_empty_project_with_core(self, project_loader):
        project_loader("empty")

        features.register(CoreFeature())
        features.register(TraefikFeature())
        load_registered_features()

        assert config.data.get('traefik.disabled') is True

    def test_install_certs(self, project_loader):
        project_loader("install-certs")

        features.register(CoreFeature())
        features.register(TraefikFeature())
        load_registered_features()

        install_action = TraefikInstalllCertsAction()
        install_action.execute(domain="dummy.tld",
                               private_key=os.path.join(".certs", "some-dummy.tld.key"),
                               certificate=os.path.join(".certs", "some-dummy.tld.crt"))

        assert os.path.exists(os.path.join(config.paths.home, "certs", "dummy.tld.key"))
        assert os.path.exists(os.path.join(config.paths.home, "certs", "dummy.tld.crt"))

        with open(os.path.join(config.paths.home, "certs", "dummy.tld.crt")) as crt_file:
            assert 'crt' == crt_file.read()

        with open(os.path.join(config.paths.home, "certs", "dummy.tld.key")) as key_file:
            assert 'key' == key_file.read()

        assert os.path.exists(os.path.join(config.data['traefik']['config_directory'], "dummy.tld.ssl.toml"))

        uninstall_action = TraefikUninstalllCertsAction()
        uninstall_action.execute(domain="dummy.tld")

        assert not os.path.exists(os.path.join(config.data['traefik']['config_directory'], "dummy.tld.ssl.toml"))

    def test_extra_services(self, project_loader):
        project_loader("extra-services")

        features.register(CoreFeature())
        features.register(TraefikFeature())
        features.register(DockerFeature())
        features.register(JsonnetFeature())
        load_registered_features()

        install_action = TraefikExtraServicesAction()
        install_action.initialize()
        install_action.execute()

        files = {
            "api": {
                "generated": "sub.project.test.extra-service.api.toml",
                "expected": "sub.project.test.extra-service.api.expected.toml"
            },
            "rule": {
                "generated": "rule.project.test.extra-service.web.toml",
                "expected": "rule.project.test.extra-service.web.expected.toml",
                "replaces": {
                    "{{ip}}": config.data.get('docker.debug.host')
                }
            },
            "secured": {
                "generated": "secured.project.test.extra-service.redirect.toml",
                "expected": "secured.project.test.extra-service.redirect.expected.toml"
            },
            "secured_path_prefix": {
                "generated": "secured.project.test.extra-service.path_prefix.toml",
                "expected": "secured.project.test.extra-service.path_prefix.expected.toml"
            },
            "secured_path_prefix_with_redirect": {
                "generated": "secured.project.test.extra-service.path_prefix_with_redirect.toml",
                "expected": "secured.project.test.extra-service.path_prefix_with_redirect.expected.toml"
            }
        }

        for file in files:
            generated = os.path.join(config.data['traefik']['config_directory'], files.get(file).get('generated'))
            assert os.path.exists(generated)
            expected = Path(
                os.path.join(config.data['traefik']['config_directory'], files.get(file).get('expected'))
            ).read_text()
            if files.get(file).get('replaces'):
                for replace in files.get(file).get('replaces'):
                    expected = expected.replace(replace, files.get(file).get('replaces').get(replace))
            assert expected == Path(generated).read_text()

    def test_extra_services_template(self, project_loader):
        project_loader("extra-services-template")

        features.register(CoreFeature())
        features.register(TraefikFeature())
        features.register(DockerFeature())
        features.register(JsonnetFeature())
        load_registered_features()

        install_action = TraefikExtraServicesAction()
        install_action.initialize()
        install_action.execute()

        api_toml = os.path.join(config.data['traefik']['config_directory'],
                                "sub.project.test.extra-service.api.toml")
        assert os.path.exists(api_toml)

        api_toml_expected = Path(os.path.join(config.data['traefik']['config_directory'],
                                              "sub.project.test.extra-service.api.expected.toml"))

        assert api_toml_expected.read_text() == Path(api_toml).read_text()

        web_toml = os.path.join(config.data['traefik']['config_directory'], "rule.project.test.extra-service.web.toml")
        assert os.path.exists(web_toml)

        web_toml_expected = Path(os.path.join(config.data['traefik']['config_directory'],
                                              "rule.project.test.extra-service.web.expected.toml"))

        assert web_toml_expected.read_text().replace('{{ip}}', config.data.get('docker.debug.host')) == Path(
            web_toml).read_text()

        secured_toml = os.path.join(config.data['traefik']['config_directory'],
                                    "secured.project.test.extra-service.redirect.toml")
        assert os.path.exists(secured_toml)

        secured_toml_expected = Path(os.path.join(config.data['traefik']['config_directory'],
                                                  "secured.project.test.extra-service.redirect.expected.toml"))

        assert secured_toml_expected.read_text() == Path(secured_toml).read_text()

    def test_extra_services_redirect(self, project_loader):
        project_loader("extra-services-redirect")

        features.register(CoreFeature())
        features.register(TraefikFeature())
        features.register(DockerFeature())
        features.register(JsonnetFeature())
        load_registered_features()

        install_action = TraefikExtraServicesAction()
        install_action.initialize()
        install_action.execute()

        api_toml = os.path.join(config.data['traefik']['config_directory'],
                                "sub.project.test.extra-service.api.toml")
        assert os.path.exists(api_toml)

        api_toml_expected = Path(os.path.join(config.data['traefik']['config_directory'],
                                              "sub.project.test.extra-service.api.expected.toml"))

        assert api_toml_expected.read_text() == Path(api_toml).read_text()

        web_toml = os.path.join(config.data['traefik']['config_directory'], "rule.project.test.extra-service.web.toml")
        assert os.path.exists(web_toml)

        web_toml_expected = Path(os.path.join(config.data['traefik']['config_directory'],
                                              "rule.project.test.extra-service.web.expected.toml"))

        assert web_toml_expected.read_text().replace('{{ip}}', config.data.get('docker.debug.host')) == Path(
            web_toml).read_text()

        secured_toml = os.path.join(config.data['traefik']['config_directory'],
                                    "secured.project.test.extra-service.no-redirect.toml")
        assert os.path.exists(secured_toml)

        secured_toml_expected = Path(os.path.join(config.data['traefik']['config_directory'],
                                                  "secured.project.test.extra-service.no-redirect.expected.toml"))

        assert secured_toml_expected.read_text() == Path(secured_toml).read_text()
