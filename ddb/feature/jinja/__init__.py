# -*- coding: utf-8 -*-
from typing import ClassVar, Iterable

from ddb.action import Action
from ddb.feature import Feature
from .actions import ConfigureAction
from .schema import JinjaSchema


class JinjaFeature(Feature):
    """
    Render template files with Jinja template engine.
    """

    @property
    def name(self) -> str:
        return "jinja"

    @property
    def schema(self) -> ClassVar[JinjaSchema]:
        return JinjaSchema

    @property
    def actions(self) -> Iterable[Action]:
        return (
            ConfigureAction(),
        )
