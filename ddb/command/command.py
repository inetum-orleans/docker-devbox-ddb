# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from argparse import ArgumentParser
from typing import Iterable, Union, Optional

from ..cache import caches
from ..config import config
from ..context import context
from ..exception import RestartWithArgs
from ..phase import phases, Phase
from ..phase.phase import execute_phase
from ..registry import RegistryObject, DefaultRegistryObject


class Command(RegistryObject, ABC):
    """
    A command is available in the program usage and can perform some action on the system.
    """

    @abstractmethod
    def execute(self):
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

    def __init__(self, name: str, description: str = None, parent: Optional[Union[Command, str]] = None):
        super().__init__(name, description)
        self._parent = parent

    @property
    def parent(self) -> Optional[Command]:
        """
        Parent command
        """
        if not self._parent:
            return None

        if isinstance(self._parent, Command):
            return self._parent

        # Inline import because of recursive imports if declared in module
        from ..command import commands  # pylint:disable=import-outside-toplevel,cyclic-import
        command = commands.get(self._parent)
        if not command:
            raise ValueError
        return command

    def execute(self):
        """
        Execute the command.
        """
        if self.parent:
            self.parent.execute()

        clear_cache = config.args.clear_cache
        if clear_cache:
            for cache in caches.all():
                cache.clear()
            config.args.clear_cache = False
            raise RestartWithArgs(config.args)

    def configure_parser(self, parser: ArgumentParser):
        """
        Configure the argument parser.
        """
        super().configure_parser(parser)
        parser.add_argument("--clear-cache", action="store_true", default=None, help="Clear all caches")


class LifecycleCommand(DefaultCommand):
    """
    A command that will emit events based on lifecycle phases.
    Triggered events are named "phase:<phase.name>"
    """

    def __init__(self, name: str, description: Union[str, None], *lifecycle: Union[str, Phase],
                 parent: Optional[Union[Command, str]] = None):
        super().__init__(name, description, parent)
        self._lifecycle = list(map(lambda phase: phases.get(phase) if not isinstance(phase, Phase) else phase,
                                   lifecycle))  # type: Iterable[Phase]

    def configure_parser(self, parser: ArgumentParser):
        super().configure_parser(parser)
        for phase in self._lifecycle:
            phase.configure_parser(parser)

    def execute(self):
        super().execute()
        for phase in self._lifecycle:
            execute_phase(phase)


def execute_command(command: Command):
    """
    Execute a command with context update.
    """

    context.command = command
    try:
        command.execute()
    finally:
        context.command = None
