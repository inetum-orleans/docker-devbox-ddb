# -*- coding: utf-8 -*-
from typing import Union, Iterable, Callable

import yaml

from .. import features
from ...action import Action
from ...config import config


class ListFeaturesAction(Action):
    """
    Display all features and their effective configuration
    """

    @property
    def event_bindings(self) -> Union[str, Iterable[Union[Iterable[str], Callable]]]:
        return "phase:info"

    @property
    def name(self) -> str:
        return "core:list-features"

    @staticmethod
    def execute():
        """
        Execute action
        """
        enabled_features = [f for f in features.all() if not f.disabled]

        print("-" * 64)
        for feature in enabled_features:
            print("name: " + feature.name)
            print("description: " + feature.description)
            print(yaml.dump(config.data.get(feature.name)), end="")
            print("-" * 64)
