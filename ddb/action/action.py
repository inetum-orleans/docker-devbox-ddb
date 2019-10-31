# -*- coding: utf-8 -*-
from abc import abstractmethod, ABC

from ddb.registry import RegistryObject


class Action(RegistryObject, ABC):
    """
    Action can perform something on the system through it's run method.
    It is executed when a particular event occurs.
    """

    @property
    @abstractmethod
    def event_name(self) -> str:
        """
        The event name that should trigger the action.
        """

    @abstractmethod
    def run(self, *args, **kwargs):
        """
        Action implementation.
        """

    @property
    def disabled(self) -> bool:
        """
        Check if the action is disabled.
        """
        return False
