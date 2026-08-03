from ..registry import Registry
from .action import Action, InitializableAction

__all__ = ["Action", "InitializableAction", "actions"]

actions = Registry(Action, "Action")  # type: Registry[Action]
