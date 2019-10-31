# -*- coding: utf-8 -*-
from typing import Iterable, ClassVar

from dotty_dict import dotty

from .actions import ListFeaturesAction
from .schema import CoreFeatureSchema
from ..feature import Feature, FeatureConfigurationAutoConfigureError
from ..schema import FeatureSchema
from ...action import Action
from ...command import LifecycleCommand, Command
from ...config import config
from ...phase import Phase, DefaultPhase


class CoreFeature(Feature):
    """
    Default commands and configuration support
    """

    @property
    def name(self) -> str:
        return "core"

    @property
    def schema(self) -> ClassVar[FeatureSchema]:
        return CoreFeatureSchema

    @property
    def actions(self) -> Iterable[Action]:
        return (
            ListFeaturesAction(),
        )

    @property
    def phases(self) -> Iterable[Phase]:
        return (
            DefaultPhase("configure", "Configure the environment"),
            DefaultPhase("create", "Create services"),
            DefaultPhase("start", "Start services"),
            DefaultPhase("init", "Initialize project",
                         lambda parser: parser.add_argument("--data", action="store_true",
                                                            help="Load testing data into services")),
            DefaultPhase("stop", "Stop services"),
            DefaultPhase("destroy", "Destroy services",
                         lambda parser: parser.add_argument("--purge", action="store_true",
                                                            help="Purge data related to services")),
            DefaultPhase("info", "List enabled features and effective configuration"),
        )

    @property
    def commands(self) -> Iterable[Command]:
        return (
            LifecycleCommand("configure", "Configure the environment", {
                "configure"
            }),

            LifecycleCommand("up", "Configure the environment, create and start services", {
                "configure", "create", "start"
            }),

            LifecycleCommand("init", "Initialize project", {
                "init"
            }),

            LifecycleCommand("down", "Stop and destroy services", {
                "stop", "destroy"
            }),

            LifecycleCommand("start", "Start services", {
                "start"
            }),

            LifecycleCommand("stop", "Stop services", {
                "stop"
            }),

            LifecycleCommand("info", "List enabled features and effective configuration", {
                "info"
            }),
        )

    def _auto_configure(self, feature_config: dict):
        feature_config = dotty(feature_config)

        env_current = 'env.current'
        env_available = 'env.available'

        if not feature_config.get(env_current) and feature_config.get(env_available):
            feature_config[env_current] = feature_config[env_available][-1]
        else:
            raise FeatureConfigurationAutoConfigureError(self, env_current)

    def before_load(self):
        config.load()
