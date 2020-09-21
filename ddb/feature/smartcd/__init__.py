# -*- coding: utf-8 -*-
from typing import Iterable, ClassVar

from ddb.action import Action
from ddb.feature import Feature
from .actions import SmartcdAction, WindowsProjectActivate


class SmartcdFeature(Feature):
    """
    Smartcd support (https://github.com/cxreg/smartcd).
    """

    @property
    def name(self) -> str:
        return "smartcd"

    @property
    def dependencies(self) -> Iterable[str]:
        return ["core"]

    @property
    def actions(self) -> Iterable[Action]:
        return (
            SmartcdAction(),
            WindowsProjectActivate(),
        )
