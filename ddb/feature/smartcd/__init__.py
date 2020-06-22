# -*- coding: utf-8 -*-
from typing import Iterable, ClassVar

from ddb.action import Action
from ddb.feature import Feature
from .actions import SmartcdAction, WindowsProjectActivate
from .schema import SmartcdSchema


class SmartcdFeature(Feature):
    """
    Generate smartcd .bash_enter/.bash_leave files to automatically activate/deactive.
    """

    @property
    def name(self) -> str:
        return "smartcd"

    @property
    def schema(self) -> ClassVar[SmartcdSchema]:
        return SmartcdSchema

    @property
    def actions(self) -> Iterable[Action]:
        return (
            SmartcdAction(),
            WindowsProjectActivate(),
        )
