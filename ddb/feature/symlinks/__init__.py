# -*- coding: utf-8 -*-
from typing import ClassVar, Iterable

from dotty_dict import Dotty

from .actions import CreateAction
from .schema import SymlinksSchema
from ..feature import Feature, FeatureConfigurationError
from ...action import Action
from ...config import config
from ...utils.file import TemplateFinder


class SymlinksFeature(Feature):
    """
    Creates symlinks from file with current environment value in their extension, or before their extension.
    """

    @property
    def name(self) -> str:
        return "symlinks"

    @property
    def dependencies(self) -> Iterable[str]:
        return ["core", "jinja[optional]"]

    @property
    def schema(self) -> ClassVar[SymlinksSchema]:
        return SymlinksSchema

    @property
    def actions(self) -> Iterable[Action]:
        return (
            CreateAction(),
        )

    def _configure_defaults(self, feature_config: Dotty):
        suffixes = feature_config.get('suffixes')
        if not suffixes:
            try:
                env_available = config.data["core.env.available"]
            except KeyError:
                raise FeatureConfigurationError(self, "core.env.available or symlinks.suffixes should be defined.")

            available_suffixes = ["." + env for env in env_available]

            env_current = config.data.get("core.env.current")
            if not env_current:
                current_suffix = available_suffixes[-1]
            else:
                current_suffix = "." + env_current

            suffixes = available_suffixes[available_suffixes.index(current_suffix):]
            feature_config["suffixes"] = suffixes

        includes = feature_config.get('includes')
        if not includes:
            includes = TemplateFinder.build_default_includes_from_suffixes(suffixes)
            feature_config["includes"] = includes
