# -*- coding: utf-8 -*-
import os
from typing import Iterable, ClassVar

from .actions import BashActivateAction, CmdActivateAction
from .schema import ShellSchema
from ..feature import Feature, FeatureConfigurationAutoConfigureError
from ..schema import FeatureSchema
from ...action import Action
from ...command import LifecycleCommand, Command
from ...phase import Phase, DefaultPhase


class ShellFeature(Feature):
    """
    Shell integration
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
            BashActivateAction(),
            CmdActivateAction()
        )

    @property
    def phases(self) -> Iterable[Phase]:
        return (
            DefaultPhase("print-activate", "Print activate script for configured shell"),
        )

    @property
    def commands(self) -> Iterable[Command]:
        return (
            LifecycleCommand("activate",
                             "Activate the shell with configured environment, and output a shell script to be executed",
                             {
                                 "configure", "print-activate"
                             }),
        )

    def _auto_configure(self, feature_config: dict):
        if 'shell' not in feature_config:
            comspec = os.environ.get('COMSPEC')
            shell = os.environ.get('SHELL')
            if comspec and comspec.endswith('cmd.exe'):
                feature_config['shell'] = 'cmd'
            elif shell and shell.endswith('bash'):
                feature_config['shell'] = 'bash'
            else:
                raise FeatureConfigurationAutoConfigureError(self, 'shell')
