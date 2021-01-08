# -*- coding: utf-8 -*-
from typing import Optional, Iterable

from ...action import Action
from ...action.action import EventBinding
from ...binary import binaries, Binary
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

        binary_set = binaries.get(name)
        binary = None
        if binary_set:
            binary = RunAction.select_binary(binary_set, *args)

        if binary:
            binary.before_run()
            events.run.command(binary.command(*args), False)
        else:
            events.run.command([name, *args], True)

    @staticmethod
    def select_binary(binary_set: Iterable[Binary], *args) -> Optional[Binary]:
        """
        Select effective binary between many binaries.
        """
        ordered_binary = sorted(binary_set)
        for binary in ordered_binary:
            if binary.should_run(*args):
                return binary
        return None
