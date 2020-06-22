# -*- coding: utf-8 -*-
from typing import Iterable, ClassVar

from ddb.action import Action
from ddb.feature import Feature
from .actions import SmartcdAction, WindowsProjectActivate


class SmartcdFeature(Feature):
    """
    Generate smartcd .bash_enter/.bash_leave files to automatically activate/deactive.
    """

    @property
    def name(self) -> str:
        return "smartcd"

    @property
    def actions(self) -> Iterable[Action]:
        return (
            SmartcdAction(),
            WindowsProjectActivate(),
        )
