# -*- coding: utf-8 -*-
import os

import yaml

from .. import features
from ...action import Action
from ...action.action import EventBinding
from ...config import config
from ...config.flatten import flatten
from ...context import context
from ...event import events


class FeaturesAction(Action):
    """
    Display all features
    """

    @property
    def event_bindings(self):
        return events.phase.features

    @property
    def name(self) -> str:
        return "core:features"

    @staticmethod
    def execute():
        """
        Execute action
        """
        enabled_features = [f for f in features.all() if not f.disabled]

        for feature in enabled_features:
            print("%s: %s" % (feature.name, feature.description))


class ConfigAction(Action):
    """
    Dump configuration
    """

    @property
    def event_bindings(self):
        return events.phase.config

    @property
    def name(self) -> str:
        return "core:config"

    @staticmethod
    def execute():
        """
        Execute action
        """
        if config.args.variables:
            flat = flatten(config.data, keep_primitive_list=True)
            for key in sorted(flat.keys()):
                print("%s: %s" % (key, flat[key]))
        else:
            print(yaml.dump(dict(config.data)))


class ReloadConfigAction(Action):
    """
    In watch mode, reload config if one configuration file is changed.
    """

    @property
    def event_bindings(self):
        def config_file_processor(file: str):
            if os.path.abspath(file) in config.files:
                return (), {"file": file}
            return None

        return (
            EventBinding(events.file.found, self.execute, config_file_processor)
        )

    @property
    def disabled(self) -> bool:
        return 'watch' not in config.args or not config.args.watch

    @property
    def name(self) -> str:
        return "core:reload-config"

    @staticmethod
    def execute(file: str):
        """
        Execute action
        """
        if context.watching:
            data = config.read()
            if data != config.loaded_data:
                try:
                    context.log.info("Configuration file has changed.")
                    config.clear()
                    config.load_from_data(data)
                    all_features = features.all()
                    for feature in all_features:
                        feature.configure()
                    context.log.info("Configuration has been reloaded.")
                    events.config.reloaded()
                except Exception as exc:  # pylint:disable=broad-except
                    context.log.warning("Configuration has fail to reload: %s", str(exc))
                    return
