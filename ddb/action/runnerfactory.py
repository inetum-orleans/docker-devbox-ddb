from .action import Action, InitializableAction
from .runner import InitializableActionEventBindingRunner, ActionEventBindingRunner, EventBindingRunner


def action_event_binding_runner_factory(action: Action, event_name: str, to_call=None, event_processor=None,
                                        fail_fast=False) -> EventBindingRunner:
    """
    Create an event binding runner from an action, event_name and optional callable.
    """
    if isinstance(action, InitializableAction):
        return InitializableActionEventBindingRunner(action, event_name, to_call, event_processor, fail_fast=fail_fast)
    return ActionEventBindingRunner(action, event_name, to_call, event_processor, fail_fast=fail_fast)
