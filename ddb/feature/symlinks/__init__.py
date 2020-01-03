# -*- coding: utf-8 -*-
from typing import ClassVar, Iterable

from dotty_dict import Dotty

from ddb.action import Action
from ddb.feature import Feature
from .actions import ConfigureAction
from .schema import SymlinksSchema
from ..feature import FeatureConfigurationError
from ...config import config


class SymlinksFeature(Feature):
    """
    Creates symlinks from file with current environment value in their extension, or before their extension.
    """

    @property
    def name(self) -> str:
        return "symlinks"

    @property
    def schema(self) -> ClassVar[SymlinksSchema]:
        return SymlinksSchema

    @property
    def actions(self) -> Iterable[Action]:
        return (
            ConfigureAction(),
        )

    def _configure_defaults(self, feature_config: Dotty):
        available_suffixes = feature_config.get("suffixes.available")

        if not available_suffixes:
            try:
                available_suffixes = config.data["core.env.available"]
            except KeyError:
                raise FeatureConfigurationError(self, "core.env.available or suffixes.available_"
                                                + "suffixes should be defined.")
            feature_config["suffixes.available"] = available_suffixes

        current_suffix = feature_config.get("suffixes.current")
        if not current_suffix:
            current_suffix = config.data.get("core.env.current")
        if not current_suffix:
            current_suffix = available_suffixes[-1]

        feature_config["suffixes.current"] = current_suffix

        if current_suffix not in available_suffixes:
            raise FeatureConfigurationError(self, "suffixes.current should be one of " + str(available_suffixes))
