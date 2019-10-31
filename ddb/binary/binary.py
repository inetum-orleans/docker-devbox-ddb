# -*- coding: utf-8 -*-
from abc import abstractmethod, ABC

from ddb.registry import RegistryObject


class Binary(RegistryObject, ABC):
    """
    Wraps a binary on the system.
    """

    @property
    @abstractmethod
    def execute(self, *args, **kwargs):
        """
        Execute the binary.
        """
