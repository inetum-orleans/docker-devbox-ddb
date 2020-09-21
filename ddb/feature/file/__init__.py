# -*- coding: utf-8 -*-
from typing import Iterable, ClassVar

from .actions import FileWalkAction
from .schema import FileSchema
from ..feature import Feature
from ..schema import FeatureSchema
from ...action import Action


class FileFeature(Feature):
    """
    Filesystem support.
    """

    @property
    def name(self) -> str:
        return "file"

    @property
    def dependencies(self) -> Iterable[str]:
        return ["core"]

    @property
    def schema(self) -> ClassVar[FeatureSchema]:
        return FileSchema

    @property
    def actions(self) -> Iterable[Action]:
        return (
            FileWalkAction(),
        )
