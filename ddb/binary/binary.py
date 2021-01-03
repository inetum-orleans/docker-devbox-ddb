# -*- coding: utf-8 -*-
from abc import abstractmethod, ABC
from typing import List, Iterable

from ddb.registry import RegistryObject


class Binary(RegistryObject, ABC):
    """
    Wraps a binary on the system.
    """

    @abstractmethod
    def command(self, *args) -> Iterable[str]:
        """
        Get the binary command
        """

    @abstractmethod
    def pre_execute(self):
        """
        Add action to be executed before running the command
        :return: True or False depending on it's the same or not
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

    def __init__(self, name: str, command: List[str]):
        super().__init__(name)
        self._command = command

    def command(self, *args) -> List[str]:
        return self._command

    def __eq__(self, other) -> bool:
        if not super().__eq__(other):
            return False
        if not isinstance(other, DefaultBinary):
            return False
        return self.command() == other.command()

    def __hash__(self):
        return hash((super().__hash__(), self.command()))

    def pre_execute(self):
        return True
