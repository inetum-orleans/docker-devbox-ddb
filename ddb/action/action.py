# -*- coding: utf-8 -*-
from abc import abstractmethod, ABC
from typing import Callable

from ddb.registry import RegistryObject


class EventBinding:
    """
    A configured event binding on action.
    """

    def __init__(self, event: str, call: Callable = None, processor: Callable = None):
        self.event = event
        self.call = call
        self.processor = processor


class Action(RegistryObject, ABC):
    """
    Action can perform something on the system through "execute" method, or any other.
    """

    @property
    @abstractmethod
    def event_bindings(self):
        """
        The event bindings that should trigger the action.

        A binding can be defined as a string matching the event name and will register the "execute" method on event
        bus.

        A binding can also be defined as a tuple.

        First value is the event name

        Second value is a callable that will be invoked with event *args, **kwargs.

        A third value may be present to process the event before invoking the callable.
        If processor returns False, callable will not be invoked.
        If processor returns a 2-tuple, it will use those as *args, **kwargs to invoke the method.

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
