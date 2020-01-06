# -*- coding: utf-8 -*-
from typing import Iterable

from ..feature import Feature


class PluginsFeature(Feature):
    """
    Load features from local python files
    """

    @property
    def name(self) -> str:
        return "plugins"

    @property
    def dependencies(self) -> Iterable[str]:
        return ["core"]
