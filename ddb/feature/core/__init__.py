# -*- coding: utf-8 -*-
import os
from argparse import ArgumentParser
from typing import Iterable, ClassVar

from dotty_dict import Dotty

from .actions import FeaturesAction, ConfigAction, ReloadConfigAction
from .schema import CoreFeatureSchema
from ..feature import Feature, FeatureConfigurationAutoConfigureError
from ..schema import FeatureSchema
from ...action import Action
from ...command import LifecycleCommand, Command
from ...config import config
from ...config.config import ConfigPaths
from ...phase import Phase, DefaultPhase


class CoreFeature(Feature):
    """
    Default commands and configuration support.
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
            FeaturesAction(),
            ConfigAction(),
            ReloadConfigAction()
        )

    @property
    def phases(self) -> Iterable[Phase]:
        def config_parser(parser: ArgumentParser):
            parser.add_argument("--variables", action="store_true",
                                help="Output as a flat list of variables available in template engines")

        def init_config_parser(parser: ArgumentParser):
            parser.add_argument("--type", action="append",
                                help="Filter for a type of information between: bin, env, port and vhost")

        return (
            DefaultPhase("init", "Initialize project", run_once=True),
            DefaultPhase("configure", "Configure the environment"),
            DefaultPhase("features", "Display enabled features"),
            DefaultPhase("config", "Display effective configuration", config_parser),
            DefaultPhase("info", "Display useful information", init_config_parser),
        )

    @property
    def commands(self) -> Iterable[Command]:
        return (
            LifecycleCommand("init", "Initialize the environment",
                             "init"),

            LifecycleCommand("configure", "Configure the environment",
                             "configure",
                             parent="init"),

            LifecycleCommand("features", "List enabled features",
                             "features"),

            LifecycleCommand("config", "Display effective configuration",
                             "config"),

            LifecycleCommand("info", "Display useful information",
                             "info"),
        )

    def configure(self):
        super().configure()
        self._load_environment_configuration()

    def _load_environment_configuration(self):
        """
        Loading enviromnent configuration file, if exists.
        """
        current = config.data.get('core.env.current')

        filenames = list(config.filenames)
        filenames.insert(1, filenames[0] + '.' + current)

        config.clear()
        config.filenames = tuple(filenames)
        config.load()
        super().configure()

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

        if not feature_config.get('path.project_home') and config.paths.project_home:
            feature_config['path.project_home'] = config.paths.project_home

        if not feature_config.get('path.home') and config.paths.home:
            feature_config['path.home'] = config.paths.home

        if not feature_config.get('path.ddb_home') and config.paths.ddb_home:
            feature_config['path.ddb_home'] = config.paths.ddb_home

        config.path = ConfigPaths(ddb_home=feature_config.get('path.ddb_home'),
                                  home=feature_config.get('path.home'),
                                  project_home=feature_config.get('path.project_home'))
