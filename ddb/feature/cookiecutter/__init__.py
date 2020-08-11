# -*- coding: utf-8 -*-
from typing import ClassVar, Iterable

from ddb.action import Action
from ddb.feature import Feature
from .actions import CookiecutterAction
from .schema import CookiecutterFeatureSchema


class CookiecutterFeature(Feature):
    """
    Generate code from a cookiecutter template available on github (https://cookiecutter.readthedocs.io).
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
