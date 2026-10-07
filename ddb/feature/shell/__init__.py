import os
from argparse import ArgumentParser
from collections.abc import Iterable
from pathlib import Path

from dotty_dict import Dotty

from ...action import Action
from ...command import Command, LifecycleCommand
from ...config import config
from ...phase import DefaultPhase, Phase
from ..feature import Feature, FeatureConfigurationAutoConfigureError
from ..schema import FeatureSchema
from .actions import (
    ActivateAction,
    CheckActivatedAction,
    CommandAction,
    CreateAliasShim,
    CreateBinaryShim,
    DeactivateAction,
)
from .integrations import BashShellIntegration, CmdShellIntegration
from .schema import ShellSchema


class ShellFeature(Feature):
    """
    Shell integration.
    """

    @property
    def name(self) -> str:
        return "shell"

    @property
    def dependencies(self) -> Iterable[str]:
        return ["core"]

    @property
    def schema(self) -> type[FeatureSchema]:
        return ShellSchema

    @property
    def actions(self) -> Iterable[Action]:
        return (
            ActivateAction(BashShellIntegration()),
            DeactivateAction(BashShellIntegration()),
            CreateBinaryShim(BashShellIntegration()),
            CreateAliasShim(BashShellIntegration()),
            CheckActivatedAction(BashShellIntegration()),
            CommandAction(BashShellIntegration()),
            ActivateAction(CmdShellIntegration()),
            DeactivateAction(CmdShellIntegration()),
            CreateBinaryShim(CmdShellIntegration()),
            CreateAliasShim(CmdShellIntegration()),
            CheckActivatedAction(CmdShellIntegration()),
            CommandAction(CmdShellIntegration()),
        )

    @property
    def phases(self) -> Iterable[Phase]:
        def activate_parser(parser: ArgumentParser) -> None:
            parser.add_argument(
                "--force", action="store_true", help="Force activation when a project is already activated."
            )

        def deactivate_parser(parser: ArgumentParser) -> None:
            parser.add_argument(
                "--force", action="store_true", help="Force deactivation when a project is already deactivated"
            )

        return (
            DefaultPhase("activate", "Write a shell script to be executed to activate environment", activate_parser),
            DefaultPhase(
                "deactivate", "Write a shell script to be executed to deactivate environment", deactivate_parser
            ),
            DefaultPhase("check-activated", "Check if project is activated in current shell"),
        )

    @property
    def commands(self) -> Iterable[Command]:
        return (
            LifecycleCommand(
                "activate",
                "Write a shell script to be executed to activate environment",
                "activate",
                avoid_stdout=True,
            ),
            LifecycleCommand(
                "deactivate",
                "Write a shell script to be executed to deactivate environment",
                "deactivate",
                avoid_stdout=True,
            ),
            LifecycleCommand(
                "check-activated",
                "Check if project is activated in current shell",
                "check-activated",
                avoid_stdout=True,
            ),
        )

    def _configure_defaults(self, feature_config: Dotty) -> None:
        if not feature_config.get("shell"):
            comspec = os.environ.get("COMSPEC")
            shell = os.environ.get("SHELL")
            if comspec and comspec.endswith("cmd.exe"):
                feature_config["shell"] = "cmd"
            elif shell and shell.endswith("bash"):
                feature_config["shell"] = "bash"
            elif shell and shell.endswith("zsh"):
                feature_config["shell"] = "zsh"
            else:
                raise FeatureConfigurationAutoConfigureError(self, "shell")

        directories = feature_config.get("path.directories")
        absolute_directories = []
        for directory in directories:
            if Path(directory).is_absolute():
                absolute_directories.append(directory)
            else:
                absolute_directory = str(Path(config.paths.project_home) / directory)
                absolute_directories.append(absolute_directory)
        feature_config["path.directories"] = absolute_directories
