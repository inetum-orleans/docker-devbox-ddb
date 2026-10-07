from ..registry import Registry
from .command import Command, LifecycleCommand

__all__ = ["Command", "LifecycleCommand", "commands"]

commands: Registry[Command] = Registry(Command, "Command")  # type: ignore[type-abstract]
