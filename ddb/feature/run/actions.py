# -*- coding: utf-8 -*-
import subprocess

from ...action import Action
from ...binary import binaries
from ...config import config


class RunAction(Action):
    """
    Run a binary
    """

    @property
    def event_bindings(self):
        return "phase:run"

    @property
    def name(self) -> str:
        return "run:run"

    @staticmethod
    def execute():
        """
        Execute action
        """
        name = config.args.name
        binary = binaries.get(name)
        print(subprocess.list2cmdline(binary.command(*config.unknown_args)))
