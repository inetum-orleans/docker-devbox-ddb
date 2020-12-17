# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from typing import Iterable, ClassVar

from .actions import SelfUpdateAction, MainCheckForUpdateAction, VersionAction
from .schema import SelfUpdateSchema
from ..feature import Feature
from ..schema import FeatureSchema
from ...action import Action
from ...command import Command, LifecycleCommand
from ...phase import DefaultPhase, Phase


class SelfUpdateFeature(Feature):
    """
    Self update support.
    """

    @property
    def name(self) -> str:
        return "selfupdate"

    @property
    def dependencies(self) -> Iterable[str]:
        return ["core"]

    @property
    def schema(self) -> ClassVar[FeatureSchema]:
        return SelfUpdateSchema

    @property
    def phases(self) -> Iterable[Phase]:
        def configure_parser(parser: ArgumentParser):
            parser.add_argument("--force", action="store_true", help="Force update")

        return (
            DefaultPhase("selfupdate", "Update ddb binary with latest version", parser=configure_parser),
        )

    @property
    def commands(self) -> Iterable[Command]:
        return (
            LifecycleCommand("self-update", "Update ddb to latest version", "selfupdate"),
        )

    @property
    def actions(self) -> Iterable[Action]:
        return (
            SelfUpdateAction(),
            MainCheckForUpdateAction(),
            VersionAction()
        )
