# -*- coding: utf-8 -*-
from typing import ClassVar, Iterable

from dotty_dict import Dotty

from ddb.action import Action
from ddb.feature import Feature
from .actions import JinjaAction
from .schema import JinjaSchema
from ...utils.file import TemplateFinder


class JinjaFeature(Feature):
    """
    Render template files with Jinja (https://jinja.palletsprojects.com).
    """

    @property
    def name(self) -> str:
        return "jinja"

    @property
    def dependencies(self) -> Iterable[str]:
        return ["file"]

    @property
    def schema(self) -> ClassVar[JinjaSchema]:
        return JinjaSchema

    @property
    def actions(self) -> Iterable[Action]:
        return (
            JinjaAction(),
        )

    def _configure_defaults(self, feature_config: Dotty):
        includes = feature_config.get("includes")
        if includes is None:
            includes = TemplateFinder.build_default_includes_from_suffixes(
                feature_config["suffixes"],
                feature_config["extensions"]
            )
            feature_config["includes"] = includes
