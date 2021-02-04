# -*- coding: utf-8 -*-
from abc import abstractmethod, ABC
from typing import Iterable, Tuple

from ddb.registry import RegistryObject


class Binary(RegistryObject, ABC):
    """
    Wraps a binary on the system.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Name of the binary.
        """

    @abstractmethod
    def command(self, *args) -> Iterable[str]:
        """
        Get the binary command.
        """

    @abstractmethod
    def should_run(self, *args) -> bool:
        """
        Check if this binary should run.
        """

    @abstractmethod
    def priority(self) -> int:
        """
        Priority of this binary amoung binaries with the same name that should run.
        """

    @abstractmethod
    def before_run(self, *args) -> None:
        """
        Add action to be executed before running the command.
        """

    @property
    @abstractmethod
    def global_(self) -> bool:
        """
        Check if binary should be registered globally.
        """

    @abstractmethod
    def __eq__(self, other) -> bool:
        pass

    @abstractmethod
    def __hash__(self):
        pass


class AbstractBinary(Binary, ABC):
    """
    Abstract implementation for binary.
    """

    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def before_run(self, *args) -> None:
        return None

    def should_run(self, *args) -> bool:
        return True

    def priority(self) -> int:
        return 0

    @property
    def global_(self) -> bool:
        return False

    def __eq__(self, other) -> bool:
        if not isinstance(other, AbstractBinary):
            return False
        return self.name == other.name

    def __hash__(self):
        return hash((self.name,))


class DefaultBinary(AbstractBinary):
    """
    Default implementation for binary.
    """

    def __init__(self, name: str, command: Iterable[str]):
        super().__init__(name)
        self._command = tuple(command)

    def command(self, *args) -> Tuple[str]:
        return self._command

    def __eq__(self, other) -> bool:
        if not super().__eq__(other):
            return False
        if not isinstance(other, DefaultBinary):
            return False
        return self.command() == other.command()

    def __hash__(self):
        return hash((super().__hash__(), self.command()))
