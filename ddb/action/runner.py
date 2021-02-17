import logging
from abc import ABC, abstractmethod
from subprocess import CalledProcessError
from typing import TypeVar, Generic

from ddb.action import Action, InitializableAction
from ddb.config import config
from ddb.context import context
from ddb.context.context import ContextStackItem

A = TypeVar('A', bound=Action)  # pylint:disable=invalid-name


class FailFastError(Exception):
    """
    A base exception that should always fail fast, even when flag is not enabled.
    """


class ExpectedError(Exception):
    """
    A base exception that can display it's own message in logs.
    """

    def log_error(self):
        """
        Log the error
        :return:
        """
        log_error = context.log.exception if \
            context.log.isEnabledFor(logging.DEBUG) or config.args.exceptions \
            else context.log.error
        log_error(str(self))


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

    def __init__(self, action: A, event_name: str, to_call=None, event_processor=None, fail_fast=False):
        super().__init__(action, event_name, to_call)
        self.event_processor = event_processor
        self.fail_fast = fail_fast

    def run(self, *args, **kwargs):  # pylint:disable=missing-function-docstring
        if self.event_processor:
            resp = self.event_processor(*args, **kwargs)
            if resp is False or resp is None:
                return None
            try:
                args, kwargs = resp
            except ValueError:
                pass

        context.stack.append(ContextStackItem(self.event_name, self.action, self.to_call, args, kwargs))
        try:
            if context.log.isEnabledFor(logging.DEBUG):
                context.log.debug("Execute action %s", context.stack)

            self._execute_action(*args, **kwargs)
            return True
        except Exception as exception:  # pylint:disable=broad-except
            self._handle_exception(exception)
            if self.fail_fast or isinstance(exception, FailFastError):
                raise
            return False
        finally:
            if context.stack:
                context.stack.pop()

    def _execute_action(self, *args, **kwargs):
        """
        Execute the action
        """
        self.to_call(*args, **kwargs)

    @staticmethod
    def _handle_exception(exception: Exception):
        """
        Handle an exception occured in an action.
        """
        context.exceptions.append(exception)
        log_error = context.log.exception if \
            context.log.isEnabledFor(logging.DEBUG) or config.args.exceptions \
            else context.log.error
        if isinstance(exception, ExpectedError):
            exception.log_error()
        else:
            log_error("An unexpected error has occured %s: %s",
                      context.stack,
                      str(exception).strip())
        if isinstance(exception, CalledProcessError):
            if exception.stderr:
                for err_line in exception.stderr.decode("utf-8").splitlines():
                    log_error("(stderr) %s", err_line)
            else:
                for out_line in exception.stderr.decode("utf-8").splitlines():
                    log_error("(output) %s", out_line)


class InitializableActionEventBindingRunner(ActionEventBindingRunner[InitializableAction]):
    """
    Runner for an initializable action event binding
    """

    def run(self, *args, **kwargs):
        """
        Initialize if required and run
        """
        if not self.action.initialized:
            self.action.initialize()
            self.action.initialized = True
        return super().run(*args, **kwargs)
