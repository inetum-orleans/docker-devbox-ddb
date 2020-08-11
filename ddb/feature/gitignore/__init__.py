# -*- coding: utf-8 -*-
from typing import ClassVar, Iterable

from ddb.action import Action
from ddb.feature import Feature
from .actions import UpdateGitignoreAction
from .schema import GitignoreSchema


class GitignoreFeature(Feature):
    """
    Update .gitignore file when a file is generated.
    """

    @property
    def name(self) -> str:
        return "gitignore"

    @property
    def schema(self) -> ClassVar[GitignoreSchema]:
        return GitignoreSchema

    @property
    def actions(self) -> Iterable[Action]:
        return (
            UpdateGitignoreAction(),
        )
