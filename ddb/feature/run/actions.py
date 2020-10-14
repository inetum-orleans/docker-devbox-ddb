# -*- coding: utf-8 -*-
import subprocess

from ...context import context
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
    def run(name: str, *args):
        """
        Execute the action
        """
        if not args:
            args = config.unknown_args

        binary = binaries.get(name)
        if binary.pre_execute():
            print(subprocess.list2cmdline(binary.command(*args)))
        else:
            context.log.error("An error occurred in pre-execution controls of the binary")
