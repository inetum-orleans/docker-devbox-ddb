from argparse import ArgumentParser
from collections.abc import Iterable

from ...action import Action
from ...command import Command
from ...command.command import LifecycleWithoutHelpCommand
from ...phase import DefaultPhase, Phase
from ..feature import Feature
from ..schema import FeatureSchema
from .actions import RunAction
from .schema import RunSchema


class RunFeature(Feature):
    """
    Run registered binaries.
    """

    @property
    def name(self) -> str:
        return "binary"

    @property
    def dependencies(self) -> Iterable[str]:
        return ["core"]

    @property
    def schema(self) -> type[FeatureSchema]:
        return RunSchema

    @property
    def phases(self) -> Iterable[Phase]:
        def run_parser(parser: ArgumentParser):
            parser.add_argument("name", help="Binary name to run")

        return (DefaultPhase("run", "Display command to run project binary", run_parser, allow_unknown_args=True),)

    @property
    def commands(self) -> Iterable[Command]:
        return (LifecycleWithoutHelpCommand("run", "Display command to run project binary", "run", avoid_stdout=True),)

    @property
    def actions(self) -> Iterable[Action]:
        return (RunAction(),)
