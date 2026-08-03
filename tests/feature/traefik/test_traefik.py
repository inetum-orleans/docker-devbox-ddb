from pathlib import Path

from ddb.__main__ import load_registered_features
from ddb.config import config
from ddb.feature import features
from ddb.feature.core import CoreFeature
from ddb.feature.docker import DockerFeature
from ddb.feature.jsonnet import JsonnetFeature
from ddb.feature.traefik import TraefikFeature
from ddb.feature.traefik.actions import (
    TraefikExtraServicesAction,
    TraefikInstalllCertsAction,
    TraefikUninstalllCertsAction,
)


class TestTraefikFeature:
    def test_empty_project_without_core(self, project_loader):
        project_loader("empty")

        features.register(TraefikFeature())
        load_registered_features()

        assert config.data.get("traefik.disabled") is True

    def test_empty_project_with_core(self, project_loader):
        project_loader("empty")

        features.register(CoreFeature())
        features.register(TraefikFeature())
        load_registered_features()

        assert config.data.get("traefik.disabled") is True

    def test_install_certs(self, project_loader):
        project_loader("install-certs")

        features.register(CoreFeature())
        features.register(TraefikFeature())
        load_registered_features()

        install_action = TraefikInstalllCertsAction()
        install_action.execute(
            domain="dummy.tld",
            private_key=str(Path(".certs") / "some-dummy.tld.key"),
            certificate=str(Path(".certs") / "some-dummy.tld.crt"),
        )

        assert (Path(config.paths.home) / "certs" / "dummy.tld.key").exists()
        assert (Path(config.paths.home) / "certs" / "dummy.tld.crt").exists()

        with (Path(config.paths.home) / "certs" / "dummy.tld.crt").open() as crt_file:
            assert crt_file.read() == "crt"

        with (Path(config.paths.home) / "certs" / "dummy.tld.key").open() as key_file:
            assert key_file.read() == "key"

        assert (Path(config.data["traefik"]["config_directory"]) / "dummy.tld.ssl.toml").exists()

        uninstall_action = TraefikUninstalllCertsAction()
        uninstall_action.execute(domain="dummy.tld")

        assert not (Path(config.data["traefik"]["config_directory"]) / "dummy.tld.ssl.toml").exists()

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
                "expected": "sub.project.test.extra-service.api.expected.toml",
            },
            "rule": {
                "generated": "rule.project.test.extra-service.web.toml",
                "expected": "rule.project.test.extra-service.web.expected.toml",
                "replaces": {"{{ip}}": config.data.get("docker.debug.host")},
            },
            "secured": {
                "generated": "secured.project.test.extra-service.redirect.toml",
                "expected": "secured.project.test.extra-service.redirect.expected.toml",
            },
            "secured_path_prefix": {
                "generated": "secured.project.test.extra-service.path_prefix.toml",
                "expected": "secured.project.test.extra-service.path_prefix.expected.toml",
            },
            "secured_path_prefix_with_redirect": {
                "generated": "secured.project.test.extra-service.path_prefix_with_redirect.toml",
                "expected": "secured.project.test.extra-service.path_prefix_with_redirect.expected.toml",
            },
        }

        for file in files:
            generated = str(Path(config.data["traefik"]["config_directory"]) / files.get(file).get("generated"))
            assert Path(generated).exists()
            expected = Path(
                str(Path(config.data["traefik"]["config_directory"]) / files.get(file).get("expected"))
            ).read_text()
            if files.get(file).get("replaces"):
                for replace in files.get(file).get("replaces"):
                    expected = expected.replace(replace, files.get(file).get("replaces").get(replace))
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

        api_toml = str(Path(config.data["traefik"]["config_directory"]) / "sub.project.test.extra-service.api.toml")
        assert Path(api_toml).exists()

        api_toml_expected = Path(
            str(Path(config.data["traefik"]["config_directory"]) / "sub.project.test.extra-service.api.expected.toml")
        )

        assert api_toml_expected.read_text() == Path(api_toml).read_text()

        web_toml = str(Path(config.data["traefik"]["config_directory"]) / "rule.project.test.extra-service.web.toml")
        assert Path(web_toml).exists()

        web_toml_expected = Path(
            str(Path(config.data["traefik"]["config_directory"]) / "rule.project.test.extra-service.web.expected.toml")
        )

        assert (
            web_toml_expected.read_text().replace("{{ip}}", config.data.get("docker.debug.host"))
            == Path(web_toml).read_text()
        )

        secured_toml = str(
            Path(config.data["traefik"]["config_directory"]) / "secured.project.test.extra-service.redirect.toml"
        )
        assert Path(secured_toml).exists()

        secured_toml_expected = Path(
            str(
                Path(config.data["traefik"]["config_directory"])
                / "secured.project.test.extra-service.redirect.expected.toml"
            )
        )

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

        api_toml = str(Path(config.data["traefik"]["config_directory"]) / "sub.project.test.extra-service.api.toml")
        assert Path(api_toml).exists()

        api_toml_expected = Path(
            str(Path(config.data["traefik"]["config_directory"]) / "sub.project.test.extra-service.api.expected.toml")
        )

        assert api_toml_expected.read_text() == Path(api_toml).read_text()

        web_toml = str(Path(config.data["traefik"]["config_directory"]) / "rule.project.test.extra-service.web.toml")
        assert Path(web_toml).exists()

        web_toml_expected = Path(
            str(Path(config.data["traefik"]["config_directory"]) / "rule.project.test.extra-service.web.expected.toml")
        )

        assert (
            web_toml_expected.read_text().replace("{{ip}}", config.data.get("docker.debug.host"))
            == Path(web_toml).read_text()
        )

        secured_toml = str(
            Path(config.data["traefik"]["config_directory"]) / "secured.project.test.extra-service.no-redirect.toml"
        )
        assert Path(secured_toml).exists()

        secured_toml_expected = Path(
            str(
                Path(config.data["traefik"]["config_directory"])
                / "secured.project.test.extra-service.no-redirect.expected.toml"
            )
        )

        assert secured_toml_expected.read_text() == Path(secured_toml).read_text()
