# -*- coding: utf-8 -*-
from typing import ClassVar, Iterable

from ddb.action import Action
from ddb.config import config
from ddb.feature import Feature
from dotty_dict import Dotty

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
    def dependencies(self) -> Iterable[str]:
        return ["core"]

    @property
    def schema(self) -> ClassVar[GitignoreSchema]:
        return GitignoreSchema

    @property
    def actions(self) -> Iterable[Action]:
        return (
            UpdateGitignoreAction(),
        )

    def _configure_defaults(self, feature_config: Dotty):
        self._configure_defaults_disabled(feature_config)

    @staticmethod
    def _configure_defaults_disabled(feature_config):
        if feature_config.get('disabled') is None:
            feature_config['disabled'] = False
            # Feature is disabled on non-dev environment.
            current = config.data.get('core.env.current')
            available = config.data.get('core.env.available')
            if current and available:
                feature_config['disabled'] = current != available[-1]
