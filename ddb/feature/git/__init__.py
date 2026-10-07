from collections.abc import Iterable

from ddb.action import Action
from ddb.feature import Feature

from .actions import FixFilePermissionsAction
from .schema import GitSchema


class GitFeature(Feature):
    """
    Git support.
    """

    @property
    def name(self) -> str:
        return "git"

    @property
    def dependencies(self) -> Iterable[str]:
        return ["core"]

    @property
    def schema(self) -> type[GitSchema]:
        return GitSchema

    @property
    def actions(self) -> Iterable[Action]:
        return (FixFilePermissionsAction(),)
