# -*- coding: utf-8 -*-
import subprocess

from ...action import Action
from ...action.action import EventBinding
from ...binary import binaries
from ...config import config
from ...event import events


class RunAction(Action):
    """
    Run a binary
    """

    @property
    def event_bindings(self):
        return (
            events.phase.run,
            EventBinding(events.run.run, self.run)
        )

    @property
    def name(self) -> str:
        return "run:run"

    @staticmethod
    def execute():
        """
        Execute the action defined by argument "name".
        """
        if hasattr(config.args, "name"):
            name = config.args.name
            events.run.run(name=name)

    @staticmethod
    def run(name: str):
        """
        Execute the action
        """

        binary = binaries.get(name)
        print(subprocess.list2cmdline(binary.command(*config.unknown_args)))
