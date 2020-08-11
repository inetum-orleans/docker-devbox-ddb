# -*- coding: utf-8 -*-
import os
from typing import Iterable, ClassVar

from dotty_dict import Dotty

from .actions import ActivateAction, DeactivateAction, CreateBinaryShim, CreateAliasShim
from .integrations import BashShellIntegration, CmdShellIntegration
from .schema import ShellSchema
from ..feature import Feature, FeatureConfigurationAutoConfigureError
from ..schema import FeatureSchema
from ...action import Action
from ...command import LifecycleCommand, Command
from ...phase import Phase, DefaultPhase


class ShellFeature(Feature):
    """
    Shell integration.
    """

    @property
    def name(self) -> str:
        return "shell"

    @property
    def schema(self) -> ClassVar[FeatureSchema]:
        return ShellSchema

    @property
    def actions(self) -> Iterable[Action]:
        return (
            ActivateAction(BashShellIntegration()),
            DeactivateAction(BashShellIntegration()),
            CreateBinaryShim(BashShellIntegration()),
            CreateAliasShim(BashShellIntegration()),
            ActivateAction(CmdShellIntegration()),
            DeactivateAction(CmdShellIntegration()),
            CreateBinaryShim(CmdShellIntegration()),
            CreateAliasShim(CmdShellIntegration()),
        )

    @property
    def phases(self) -> Iterable[Phase]:
        return (
            DefaultPhase("activate", "Write a shell script to be executed to activate environment"),
            DefaultPhase("deactivate", "Write a shell script to be executed to deactivate environment")
        )

    @property
    def commands(self) -> Iterable[Command]:
        return (
            LifecycleCommand("activate",
                             "Write a shell script to be executed to activate environment",
                             "activate"
                             ),
            LifecycleCommand("deactivate",
                             "Write a shell script to be executed to deactivate environment",
                             "deactivate"
                             ),
        )

    def _configure_defaults(self, feature_config: Dotty):
        if 'shell' not in feature_config:
            comspec = os.environ.get('COMSPEC')
            shell = os.environ.get('SHELL')
            if comspec and comspec.endswith('cmd.exe'):
                feature_config['shell'] = 'cmd'
            elif shell and shell.endswith('bash'):
                feature_config['shell'] = 'bash'
            elif shell and shell.endswith('zsh'):
                feature_config['shell'] = 'zsh'
            else:
                raise FeatureConfigurationAutoConfigureError(self, 'shell')
