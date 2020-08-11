# -*- coding: utf-8 -*-
from typing import ClassVar, Iterable

from dotty_dict import Dotty

from ddb.action import Action
from ddb.feature import Feature
from .actions import JsonnetAction
from .schema import JsonnetSchema
from ...utils.file import TemplateFinder


class JsonnetFeature(Feature):
    """
    Render template files with Jsonnet (https://jsonnet.org).
    """

    @property
    def name(self) -> str:
        return "jsonnet"

    @property
    def dependencies(self) -> Iterable[str]:
        return ["file"]

    @property
    def schema(self) -> ClassVar[JsonnetSchema]:
        return JsonnetSchema

    @property
    def actions(self) -> Iterable[Action]:
        return (
            JsonnetAction(),
        )

    def _configure_defaults(self, feature_config: Dotty):
        includes = feature_config.get("includes")
        if includes is None:
            includes = TemplateFinder.build_default_includes_from_suffixes(
                feature_config["suffixes"],
                feature_config["extensions"]
            )
            feature_config["includes"] = includes
