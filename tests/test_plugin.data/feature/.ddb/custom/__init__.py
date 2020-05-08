# -*- coding: utf-8 -*-
from typing import Iterable

from ddb.action import Action
from ddb.feature import Feature
from .actions import CustomAction


class CustomFeature(Feature):
    """
    Custom Feature
    """

    @property
    def name(self) -> str:
        return "custom"

    @property
    def actions(self) -> Iterable[Action]:
        return (
            CustomAction(),
        )
