# -*- coding: utf-8 -*-
from typing import Iterable, ClassVar

from .actions import FixuidDockerComposeAction
from .schema import FixuidSchema
from ..feature import Feature
from ..schema import FeatureSchema
from ...action import Action


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
        return (
            FixuidDockerComposeAction(),
        )
