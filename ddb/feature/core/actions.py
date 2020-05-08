# -*- coding: utf-8 -*-
import yaml

from .. import features
from ...action import Action
from ...config import config
from ...config.flatten import flatten
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
            flat = flatten(config.data, stop_for_features=features.all())
            for key in sorted(flat.keys()):
                print("%s: %s" % (key, flat[key]))
        else:
            print(yaml.dump(dict(config.data)))
