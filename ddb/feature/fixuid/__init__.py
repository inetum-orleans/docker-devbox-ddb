from collections.abc import Iterable
from typing import ClassVar

from ...action import Action
from ..feature import Feature
from ..schema import FeatureSchema
from .actions import FixuidDockerComposeAction
from .schema import FixuidSchema


class FixuidFeature(Feature):
    """
    Auto-configure fixuid from docker-compose.yml services (https://github.com/boxboat/fixuid)
    """

    @property
    def name(self) -> str:
        return "fixuid"

    @property
    def dependencies(self) -> Iterable[str]:
        return ["core", "docker[optional]"]

    @property
    def schema(self) -> ClassVar[FeatureSchema]:
        return FixuidSchema

    @property
    def actions(self) -> Iterable[Action]:
        return (FixuidDockerComposeAction(),)
