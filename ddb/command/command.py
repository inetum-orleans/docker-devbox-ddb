# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from argparse import ArgumentParser
from typing import Iterable, Union, Optional, Callable, Any

from ..context import context
from ..phase import phases, Phase
from ..phase.phase import execute_phase
from ..registry import RegistryObject, DefaultRegistryObject


class Command(RegistryObject, ABC):
    """
    A command is available in the program usage and can perform some action on the system.
    """

    @property
    @abstractmethod
    def allow_unknown_args(self):
        """
        Check if this command allow unknown args.
        """

    @property
    @abstractmethod
    def avoid_stdout(self):
        """
        Should this command avoid stdout spoiling
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

    def add_parser(self, subparsers):
        """
        Add command parser into given subparsers.
        """
        return subparsers.add_parser(self.name, help=self.description)


class DefaultCommand(DefaultRegistryObject, Command):
    """
    A command is available in the program usage and can perform some action on the system.
    """

    def __init__(self, name: str, description: str = None, parent: Optional[Union[Command, str]] = None,
                 allow_unknown_args=False, before_execute: Optional[Callable[[], Any]] = None, avoid_stdout=False):
        super().__init__(name, description)
        self.before_execute = before_execute
        self._parent = parent
        self._allow_unknown_args = allow_unknown_args
        self._avoid_stdout = avoid_stdout

    @property
    def allow_unknown_args(self):
        return self._allow_unknown_args

    @property
    def avoid_stdout(self):
        return self._avoid_stdout

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
        if self.before_execute:
            self.before_execute()

        if self.parent:
            self.parent.execute()


class LifecycleCommand(DefaultCommand):
    """
    A command that will emit events based on lifecycle phases.
    Triggered events are named "phase:<phase.name>"
    """

    def __init__(self, name: str, description: Union[str, None], *lifecycle: Union[str, Phase],
                 parent: Optional[Union[Command, str]] = None, before_execute: Optional[Callable[[], Any]] = None,
                 avoid_stdout=False):
        super().__init__(name, description, parent, before_execute=before_execute, avoid_stdout=avoid_stdout)
        self._lifecycle = list(map(lambda phase: phases.get(phase) if not isinstance(phase, Phase) else phase,
                                   lifecycle))  # type: Iterable[Phase]
        for phase in self._lifecycle:
            if phase.allow_unknown_args:
                self._allow_unknown_args = True

    def configure_parser(self, parser: ArgumentParser):
        super().configure_parser(parser)
        for phase in self._lifecycle:
            phase.configure_parser(parser)

    def execute(self):
        super().execute()
        for phase in self._lifecycle:
            execute_phase(phase)


class LifecycleWithoutHelpCommand(LifecycleCommand):
    """
    A LifecycleCommand that doesn't add --help option to it's parser.
    """

    def add_parser(self, subparsers):
        """
        Add command parser into given subparsers.
        """
        return subparsers.add_parser(self.name, help=self.description, add_help=False)


def execute_command(command: Command):
    """
    Execute a command with context update.
    """

    context.command = command
    try:
        command.execute()
    finally:
        context.command = None
