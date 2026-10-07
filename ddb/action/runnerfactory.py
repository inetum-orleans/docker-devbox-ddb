from collections.abc import Callable
from typing import Any

from .action import Action, InitializableAction
from .runner import ActionEventBindingRunner, EventBindingRunner, InitializableActionEventBindingRunner


def action_event_binding_runner_factory(
    action: Action,
    event_name: str,
    to_call: Callable[..., Any] | None = None,
    event_processor: Callable[..., Any] | None = None,
    *,
    fail_fast: bool = False,
) -> EventBindingRunner[Any]:
    """
    Create an event binding runner from an action, event_name and optional callable.
    """
    if isinstance(action, InitializableAction):
        return InitializableActionEventBindingRunner(action, event_name, to_call, event_processor, fail_fast=fail_fast)
    return ActionEventBindingRunner(action, event_name, to_call, event_processor, fail_fast=fail_fast)
