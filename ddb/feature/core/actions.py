# -*- coding: utf-8 -*-
import yaml

from .. import features
from ...action import Action
from ...config import config


class ListFeaturesAction(Action):
    """
    Display all features and their effective configuration
    """

    @property
    def event_name(self) -> str:
        return "phase:info"

    @property
    def name(self) -> str:
        return "list-features"

    def run(self, *args, **kwargs):
        enabled_features = [f for f in features.all() if not f.disabled]

        print("-" * 64)
        for feature in enabled_features:
            print("name: " + feature.name)
            print("description: " + feature.description)
            print(yaml.dump(config.data.get(feature.name)), end="")
            print("-" * 64)
