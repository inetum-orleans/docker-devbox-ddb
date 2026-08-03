from collections.abc import Iterable
from pathlib import Path

from dotty_dict import Dotty

from ...action import Action
from ...config import config
from ..feature import Feature, FeatureConfigurationAutoConfigureError
from ..schema import FeatureSchema
from .actions import TraefikExtraServicesAction, TraefikInstalllCertsAction, TraefikUninstalllCertsAction
from .schema import TraefikSchema


class TraefikFeature(Feature):
    """
    Traefik support (https://traefik.io).
    """

    @property
    def name(self) -> str:
        return "traefik"

    @property
    def dependencies(self) -> Iterable[str]:
        return ["core", "certs[optional]"]

    @property
    def schema(self) -> type[FeatureSchema]:
        return TraefikSchema

    @property
    def actions(self) -> Iterable[Action]:
        return (
            TraefikInstalllCertsAction(),
            TraefikUninstalllCertsAction(),
            TraefikExtraServicesAction(),
            # TODO: Add action to install custom traefik configuration
        )

    def _configure_defaults(self, feature_config: Dotty):
        certs_directory = feature_config.get("certs_directory")
        if not certs_directory and config.paths.home:
            certs_directory = str(Path(config.paths.home) / "certs")
            if Path(certs_directory).exists():
                feature_config["certs_directory"] = certs_directory

        config_directory = feature_config.get("config_directory")
        if not config_directory and config.paths.home:
            config_directory = str(Path(config.paths.home) / "traefik" / "config")
            if Path(config_directory).exists():
                feature_config["config_directory"] = config_directory

            config_directory = str(Path(config.paths.home) / "docker-toolbox" / ".docker" / "traefik" / "hosts")
            if Path(config_directory).exists():
                feature_config["config_directory"] = config_directory

        extra_services = feature_config.get("extra_services")
        if extra_services:
            for extra_service in extra_services.values():
                domain = extra_service.get("domain")
                if not extra_service.get("rule"):
                    if not domain:
                        raise FeatureConfigurationAutoConfigureError(
                            self, "extra_services", "domain must be defined when rule is not defined."
                        )
                    extra_service["rule"] = f"Host(`{domain}`)"
                if extra_service.get("https") is not False and not domain:
                    raise FeatureConfigurationAutoConfigureError(
                        self, "extra_services", "domain must be defined when https is not False."
                    )

        if not feature_config.get("config_directory"):
            feature_config["disabled"] = True
