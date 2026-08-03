from collections.abc import Iterable
from typing import ClassVar

from ...action import Action
from ..feature import Feature
from ..schema import FeatureSchema
from .actions import FileWalkAction
from .schema import FileSchema


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
