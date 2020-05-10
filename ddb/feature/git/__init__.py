# -*- coding: utf-8 -*-
from typing import ClassVar, Iterable

from ddb.action import Action
from ddb.feature import Feature
from .actions import FixFilePermissionsAction
from .schema import GitSchema


class GitFeature(Feature):
    """
    Update gitignore files when a file is generated.
    """

    @property
    def name(self) -> str:
        return "git"

    @property
    def schema(self) -> ClassVar[GitSchema]:
        return GitSchema

    @property
    def actions(self) -> Iterable[Action]:
        return (
            FixFilePermissionsAction(),
        )
