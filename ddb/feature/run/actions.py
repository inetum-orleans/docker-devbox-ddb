# -*- coding: utf-8 -*-
import subprocess
from typing import Union, Iterable, Callable

from ...action import Action
from ...binary import binaries
from ...config import config


class RunAction(Action):
    """
    Run a binary
    """

    @property
    def event_bindings(self) -> Union[str, Iterable[Union[Iterable[str], Callable]]]:
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
