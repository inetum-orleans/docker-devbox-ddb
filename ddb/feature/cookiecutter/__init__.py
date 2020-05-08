# -*- coding: utf-8 -*-
from typing import ClassVar, Iterable

from ddb.action import Action
from ddb.feature import Feature
from .actions import CookiecutterAction
from .schema import CookiecutterFeatureSchema


class CookiecutterFeature(Feature):
    """
    Grabs templates from github repositories with semver versioning.
    """

    @property
    def name(self) -> str:
        return "cookiecutter"

    @property
    def schema(self) -> ClassVar[CookiecutterFeatureSchema]:
        return CookiecutterFeatureSchema

    @property
    def actions(self) -> Iterable[Action]:
        return (
            CookiecutterAction(),
        )
