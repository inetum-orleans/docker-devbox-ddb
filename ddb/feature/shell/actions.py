# -*- coding: utf-8 -*-
import os

from ...action import Action
from ...config import config


class BashActivateAction(Action):
    """
    Print activate script for Bash
    """

    @property
    def event_name(self) -> str:
        return "phase:print-activate"

    @property
    def name(self) -> str:
        return "bash-integration"

    @property
    def disabled(self) -> bool:
        return config.data.get('shell.shell') != 'bash'

    def run(self, *args, **kwargs):
        for (name, value) in os.environ.items():
            print("EXPORT " + name + "=" + value)


class CmdActivateAction(Action):
    """
    Print activate script for Windows cmd.exe
    """

    @property
    def event_name(self) -> str:
        return "phase:print-activate"

    @property
    def name(self) -> str:
        return "cmd-integration"

    @property
    def disabled(self) -> bool:
        return config.data.get('shell.shell') != 'cmd'

    def run(self, *args, **kwargs):
        for (name, value) in os.environ.items():
            print("SET " + name + "=" + value)
