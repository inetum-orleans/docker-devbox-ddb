# -*- coding: utf-8 -*-
from ..feature import Feature


class PluginsFeature(Feature):
    """
    Load features from local python files
    """

    @property
    def name(self) -> str:
        return "plugins"
