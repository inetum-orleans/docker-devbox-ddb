# -*- coding: utf-8 -*-
from typing import Iterable

from abc import abstractmethod, ABC

from ddb.context import context
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
    def execute(self, *args, **kwargs):
        """
        Action implementation. *args and **kwargs are coming from the provided command line arguments.
        """

    @property
    def order(self) -> int:
        """
        The order index related to this action.

        When many actions are registered on the same event name, they will be executed in sequence following the
        natural ordering from this value.
        """
        return 0

    def execute_in_context(self, *args, **kwargs):
        """
        Execute action implementation with context update.
        """
        execute_action(self, *args, **kwargs)

    @property
    def disabled(self) -> bool:
        """
        Check if the action is disabled.
        """
        return False


def execute_action(action: Action, *args, **kwargs):
    """
    Execute an action with context update.
    """

    context.action = action
    try:
        action.execute(*args, **kwargs)
    finally:
        context.action = None
