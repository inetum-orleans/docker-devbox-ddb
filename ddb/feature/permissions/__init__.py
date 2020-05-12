# -*- coding: utf-8 -*-
from typing import ClassVar, Iterable

from ddb.action import Action
from ddb.feature import Feature
from .actions import PermissionsAction
from .schema import PermissionsSchema


class PermissionsFeature(Feature):
    """
    Update gitignore files when a file is generated.
    """

    @property
    def name(self) -> str:
        return "permissions"

    @property
    def schema(self) -> ClassVar[PermissionsSchema]:
        return PermissionsSchema

    @property
    def actions(self) -> Iterable[Action]:
        return (
            PermissionsAction(),
        )
