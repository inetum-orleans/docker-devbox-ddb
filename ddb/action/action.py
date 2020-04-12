# -*- coding: utf-8 -*-
from abc import abstractmethod, ABC
from typing import Iterable, Union, Callable

from ddb.registry import RegistryObject


class Action(RegistryObject, ABC):
    """
    Action can perform something on the system through "execute" method, or any other.
    """

    @property
    @abstractmethod
    def event_bindings(self) -> Union[str, Iterable[Union[Iterable[str], Callable]]]:
        """
        The event bindings that should trigger the action.

        A binding can be defined as a string matching the event name and will register the "execute" method on event
        bus.

        A binding can also be defined as a 2-tuple of string, first value matching the event name and will register
        the method named from second value on event bus.

        This method returns an iterable of bindings.
        """

    @property
    def order(self) -> int:
        """
        The order index related to this action.

        When many actions are registered on the same event name, they will be executed in sequence following the
        natural ordering from this value.
        """
        return 0

    @property
    def disabled(self) -> bool:
        """
        Check if the action is disabled.
        """
        return False


class InitializableAction(Action, ABC):  # pylint:disable=abstract-method
    """
    An action supporting an initialize singleton method.
    """

    def __init__(self):
        self.initialized = False

    def initialize(self):
        """
        Initialize method, invoked before first event binding execution.
        """
