# -*- coding: utf-8 -*-
import os
from typing import Iterable, ClassVar

from dotty_dict import Dotty

from .actions import TraefikInstalllCertsAction, TraefikUninstalllCertsAction
from .schema import TraefikSchema
from ..feature import Feature
from ..schema import FeatureSchema
from ...action import Action
from ...config import config


class TraefikFeature(Feature):
    """
    Traefik support (https://traefik.io).
    """

    @property
    def name(self) -> str:
        return "traefik"

    @property
    def schema(self) -> ClassVar[FeatureSchema]:
        return TraefikSchema

    @property
    def dependencies(self) -> Iterable[str]:
        return ["certs[optional]"]

    @property
    def actions(self) -> Iterable[Action]:
        return (
            TraefikInstalllCertsAction(),
            TraefikUninstalllCertsAction()
            # TODO: Add action to install custom traefik configuration
        )

    def _configure_defaults(self, feature_config: Dotty):
        certs_directory = feature_config.get('certs_directory')
        if not certs_directory and config.paths.home:
            certs_directory = os.path.join(config.paths.home, 'certs')
            if os.path.exists(certs_directory):
                feature_config['certs_directory'] = certs_directory

        config_directory = feature_config.get('config_directory')
        if not config_directory and config.paths.home:
            config_directory = os.path.join(config.paths.home, 'traefik', 'config')
            if os.path.exists(config_directory):
                feature_config['config_directory'] = config_directory

        if not feature_config.get('config_directory'):
            feature_config['disabled'] = True
