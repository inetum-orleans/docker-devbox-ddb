# -*- coding: utf-8 -*-
import os
from typing import Iterable, ClassVar

from dotty_dict import Dotty

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
            DefaultPhase("pre-init", "Initialize project (pre)", run_once=True),
            DefaultPhase("init", "Initialize project", run_once=True),
            DefaultPhase("post-init", "Initialize project (post)", run_once=True),

            DefaultPhase("pre-configure", "Configure the environment (pre)"),
            DefaultPhase("configure", "Configure the environment"),
            DefaultPhase("post-configure", "Configure the environment (post)"),

            DefaultPhase("pre-create", "Create services (pre)"),
            DefaultPhase("create", "Create services"),
            DefaultPhase("post-create", "Create services (post)"),

            DefaultPhase("start", "Start services",
                         lambda parser: parser.add_argument("--data", action="store_true",
                                                            help="Load data into services")),
            DefaultPhase("stop", "Stop services"),
            DefaultPhase("down", "Destroy services",
                         lambda parser: parser.add_argument("--purge", action="store_true",
                                                            help="Purge data from services")),
            DefaultPhase("info", "List enabled features and effective configuration"),
        )

    @property
    def commands(self) -> Iterable[Command]:
        return (
            LifecycleCommand("init", "Initialize the environment",
                             "pre-init", "init", "post-init"
                             ),

            LifecycleCommand("configure", "Configure the environment",
                             "pre-configure", "configure", "post-configure",
                             parent="init"
                             ),

            LifecycleCommand("create", "Configure the environment and create services",
                             "pre-create", "create", "post-create",
                             parent="configure"
                             ),

            LifecycleCommand("up", "Configure the environment, create and start services",
                             "start",
                             parent="create"
                             ),

            LifecycleCommand("start", "Start services",
                             "start",
                             ),

            LifecycleCommand("stop", "Stop services",
                             "stop",
                             ),

            LifecycleCommand("down", "Stop and destroy services",
                             "down",
                             parent="stop"
                             ),

            LifecycleCommand("info", "List enabled features and effective configuration",
                             "info"
                             ),
        )

    def _configure_defaults(self, feature_config: Dotty):
        if not feature_config.get('project.name'):
            project_name = os.path.basename(config.paths.project_home)
            feature_config['project.name'] = project_name

        if not feature_config.get('domain.sub'):
            feature_config['domain.sub'] = feature_config['project.name'].replace("_", "-").replace(" ", "-")

        if not feature_config.get('env.current') and feature_config.get('env.available'):
            feature_config['env.current'] = feature_config['env.available'][-1]

        if not feature_config.get('env.current') or \
                feature_config.get('env.current') not in feature_config['env.available']:
            raise FeatureConfigurationAutoConfigureError(self, 'env.current')

    def before_load(self):
        config.load()
