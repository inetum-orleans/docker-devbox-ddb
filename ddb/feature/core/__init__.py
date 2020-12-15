# -*- coding: utf-8 -*-
import os
from argparse import ArgumentParser
from typing import Iterable, ClassVar

from dotty_dict import Dotty

from .actions import FeaturesAction, ConfigAction, ReloadConfigAction, EjectAction
from .schema import CoreFeatureSchema
from ..feature import Feature, FeatureConfigurationAutoConfigureError
from ..schema import FeatureSchema
from ...action import Action
from ...command import LifecycleCommand, Command
from ...config import config
from ...config.config import ConfigPaths
from ...phase import Phase, DefaultPhase


class ConfigureSecondPassException(Exception):
    """
    Exception that should be raised when an additional configuration file is to be loaded.
    """


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
            ReloadConfigAction(),
            EjectAction()
        )

    @property
    def phases(self) -> Iterable[Phase]:
        def configure_parser(parser: ArgumentParser):
            parser.add_argument("--eject", action="store_true",
                                help="Eject the project using the current configuration")

        def config_parser(parser: ArgumentParser):
            parser.add_argument("--variables", action="store_true",
                                help="Output as a flat list of variables available in template engines")

        def info_parser(parser: ArgumentParser):
            parser.add_argument("--type", action="append",
                                help="Filter for a type of information between: bin, env, port and vhost")

        return (
            DefaultPhase("init", "Initialize project", run_once=True),
            DefaultPhase("configure", "Configure the environment", configure_parser),
            DefaultPhase("features", "Display enabled features"),
            DefaultPhase("config", "Display effective configuration", config_parser),
            DefaultPhase("info", "Display useful information", info_parser),
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

    def configure(self, bootstrap=False):
        super().configure(bootstrap)
        if bootstrap:
            return
        self._load_environment_configuration()
        self._apply_eject_configuration()

    @staticmethod
    def _load_environment_configuration():
        """
        Loading enviromnent configuration file, if exists.
        """
        current = config.data.get('core.env.current')

        if config.filenames:
            filenames = list(config.filenames)
            original_filenames = list(config.filenames)

            current_env_filename = filenames[0] + '.' + current
            if current_env_filename not in filenames:
                filenames.insert(len(filenames) - 1, current_env_filename)

            extra = config.data.get('core.configuration.extra')
            if extra:
                for extra_item in extra:
                    if extra_item not in filenames:
                        filenames.insert(len(filenames) - 1, extra_item)

            if filenames != original_filenames:
                config.filenames = tuple(filenames)

                raise ConfigureSecondPassException()

    @staticmethod
    def _apply_eject_configuration():
        """
        Override some configuration that doesn't make sense without ddb
        :return:
        """
        if config.eject:
            config.data['core.path.ddb_home'] = '.ddb-home'
            config.data['core.path.home'] = '.docker-devbox-home'
            config.data['core.path.project_home'] = '.'

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
