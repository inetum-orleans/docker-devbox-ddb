# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from argparse import ArgumentParser
from typing import Iterable, Union

from ..cache import caches
from ..context import context
from ..phase import phases, Phase
from ..phase.phase import execute_phase
from ..registry import RegistryObject, DefaultRegistryObject


class Command(RegistryObject, ABC):
    """
    A command is available in the program usage and can perform some action on the system.
    """

    @abstractmethod
    def execute(self, *args, **kwargs):
        """
        Execute the command.
        """

    def configure_parser(self, parser: ArgumentParser):
        """
        Configure the argument parser.
        """


class DefaultCommand(DefaultRegistryObject, Command):
    """
    A command is available in the program usage and can perform some action on the system.
    """

    def execute(self, *args, **kwargs):
        """
        Execute the command.
        """
        clear_cache = kwargs.get("clear_cache")
        if clear_cache:
            for cache in caches.all():
                cache.clear()

    def configure_parser(self, parser: ArgumentParser):
        """
        Configure the argument parser.
        """
        super().configure_parser(parser)
        parser.add_argument("--clear-cache", action="store_true", help="Clear all caches")


class LifecycleCommand(DefaultCommand):
    """
    A command that will emit events based on lifecycle phases.
    Triggered events are named "phase:<phase.name>"
    """

    def __init__(self, name: str, description: Union[str, None], *lifecycle: Union[str, Phase]):
        super().__init__(name, description)
        self._lifecycle = list(map(lambda phase: phases.get(phase) if not isinstance(phase, Phase) else phase,
                                   lifecycle))  # type: Iterable[Phase]

    def configure_parser(self, parser: ArgumentParser):
        super().configure_parser(parser)
        for phase in self._lifecycle:
            phase.configure_parser(parser)

    def execute(self, *args, **kwargs):
        super().execute(*args, **kwargs)
        for phase in self._lifecycle:
            execute_phase(phase, *args, **kwargs)


def execute_command(command: Command, *args, **kwargs):
    """
    Execute a command with context update.
    """

    context.command = command
    try:
        command.execute(*args, **kwargs)
    finally:
        context.command = None
