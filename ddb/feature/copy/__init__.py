from collections.abc import Iterable

from ...action import Action
from ..feature import Feature
from ..schema import FeatureSchema
from .actions import CopyAction
from .schema import CopySchema


class CopyFeature(Feature):
    """
    Copy files from local filesystem or remote URL to one or many directories.
    """

    @property
    def name(self) -> str:
        return "copy"

    @property
    def dependencies(self) -> Iterable[str]:
        return ["core"]

    @property
    def schema(self) -> type[FeatureSchema]:
        return CopySchema

    @property
    def actions(self) -> Iterable[Action]:
        return (CopyAction(),)
