import logging
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
    def __init__(self, action: A, event_name: str, to_call=None, fail_fast=False):
        super().__init__(action, event_name, to_call)
        self.fail_fast = fail_fast

    def run(self, *args, **kwargs):  # pylint:disable=missing-function-docstring
        context.actions.append(self.action)
        parameters_repr = None
        try:
            if context.log.isEnabledFor(logging.DEBUG):
                parameters_repr = self._build_parameters_repr(*args, **kwargs)
                context.log.debug("Execute action [%s => %s.%s(%s)]",
                                  self.event_name,
                                  type(self.action).__name__,
                                  self.to_call.__name__,
                                  parameters_repr)

            self._execute_action(*args, **kwargs)
        except Exception as exception:  # pylint:disable=broad-except
            if not parameters_repr:
                parameters_repr = self._build_parameters_repr(*args, **kwargs)

            context.exceptions.append(exception)
            log_error = context.log.exception if context.log.isEnabledFor(logging.DEBUG) else context.log.error
            log_error("An unexpected error has occured [%s => %s.%s(%s)]: %s",
                      self.event_name,
                      type(self.action).__name__,
                      self.to_call.__name__,
                      parameters_repr,
                      str(exception).strip())

            if self.fail_fast:
                raise

        finally:
            context.actions.pop()

    def _execute_action(self, *args, **kwargs):
        """
        Execute the action
        """
        self.to_call(*args, **kwargs)

    @staticmethod
    def _build_parameters_repr(*args, **kwargs):
        parameters_repr = ', '.join(args)
        for key, value in sorted(kwargs.items()):
            if parameters_repr:
                parameters_repr += ', '
            parameters_repr += key + "=" + str(value)
        return parameters_repr


class InitializableActionEventBindingRunner(ActionEventBindingRunner[InitializableAction]):
    """
    Runner for an initializable action event binding
    """

    def _execute_action(self, *args, **kwargs):
        if not self.action.initialized:
            self.action.initialize()
            self.action.initialized = True
        super()._execute_action(*args, **kwargs)
