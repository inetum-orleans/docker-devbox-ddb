# -*- coding: utf-8 -*-
from typing import Iterable, Union, Callable

from abc import abstractmethod, ABC

from ddb.context import context
from ddb.registry import RegistryObject


class Action(RegistryObject, ABC):
    """
    Action can perform something on the system through it's run method.
    It is executed when a particular event occurs.
    """

    def __init__(self):
        self._initialized = False

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

    @abstractmethod
    def execute(self, *args, **kwargs):
        """
        Action implementation. *args and **kwargs are coming from the provided command line arguments.
        """

    def initialize(self):
        """
        Initialize method, invoked before first event binding execution.
        """

    @property
    def order(self) -> int:
        """
        The order index related to this action.

        When many actions are registered on the same event name, they will be executed in sequence following the
        natural ordering from this value.
        """
        return 0

    def execute_event_binding_factory(self, to_call=None):
        """
        Factory to create a ready to register function on event bus.
        """
        if not to_call:
            to_call = self.execute

        def execute_event_binding(*args, **kwargs):
            context.action = self
            try:
                if not self._initialized:
                    self.initialize()
                    self._initialized = True
                to_call(*args, **kwargs)
            finally:
                context.action = None

        return execute_event_binding

    @property
    def disabled(self) -> bool:
        """
        Check if the action is disabled.
        """
        return False
