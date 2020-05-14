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
    def is_same(self, binary) -> bool:
        """
        Check if given binary is the same as the current one
        :param binary: Binary object
        :return: True or False depending on it's the same or not
        """

class DefaultBinary(Binary):
    """
    Default implementation for binary.
    """

    def __init__(self, name: str, command: List[str]):
        self._name = name
        self._command = command

    @property
    def name(self) -> str:
        return self._name

    def command(self, *args) -> List[str]:
        return self._command

    def is_same(self, binary) -> bool:
        return self.command() == binary.command()
