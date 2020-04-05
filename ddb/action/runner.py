from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from ddb.action import Action, InitializableAction
from ddb.context import context

A = TypeVar('A', bound=Action)  # pylint:disable=invalid-name

# pylint:disable=too-few-public-methods


class EventBindingRunner(Generic[A], ABC):
    """
    Runner for an event binding.
    """
    def __init__(self, action: A, event_name: str, to_call=None):
        self.action = action
        self.event_name = event_name
        self.to_call = to_call if to_call else action.execute

    @abstractmethod
    def run(self, *args, **kwargs):
        """
        Run the callable registered on this event binding.
        """


class ActionEventBindingRunner(Generic[A], EventBindingRunner[A]):
    """
    Runner for an action event binding.
    """
    def run(self, *args, **kwargs):  # pylint:disable=missing-function-docstring
        context.actions.append(self.action)
        try:
            context.log.debug("Run event binding: %s => %s", self.event_name, str(self.to_call))
            self._execute_action(*args, **kwargs)
        finally:
            context.actions.pop()

    def _execute_action(self, *args, **kwargs):
        """
        Execute the action
        """
        context.log.debug("Execute action")
        self.to_call(*args, **kwargs)


class InitializableActionEventBindingRunner(ActionEventBindingRunner[InitializableAction]):
    """
    Runner for an initializable action event binding
    """
    def _execute_action(self, *args, **kwargs):
        if not self.action.initialized:
            context.log.debug("Initialize")
            self.action.initialize()
            self.action.initialized = True
        super()._execute_action(*args, **kwargs)
