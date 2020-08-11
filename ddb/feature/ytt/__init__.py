# -*- coding: utf-8 -*-
from typing import ClassVar, Iterable

from dotty_dict import Dotty

from ddb.action import Action
from ddb.feature import Feature
from .actions import YttAction
from .schema import YttSchema
from ...utils.file import TemplateFinder


class YttFeature(Feature):
    """
    Render template files with ytt (https://get-ytt.io/).
    """

    @property
    def name(self) -> str:
        return "ytt"

    @property
    def dependencies(self) -> Iterable[str]:
        return ["file"]

    @property
    def schema(self) -> ClassVar[YttSchema]:
        return YttSchema

    @property
    def actions(self) -> Iterable[Action]:
        return (
            YttAction(),
        )

    def _configure_defaults(self, feature_config: Dotty):
        includes = feature_config.get("includes")
        if includes is None:
            includes = TemplateFinder.build_default_includes_from_suffixes(
                feature_config["suffixes"],
                feature_config["extensions"]
            )
            feature_config["includes"] = includes
