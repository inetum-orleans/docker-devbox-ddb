from ..registry import Registry
from .command import Command, LifecycleCommand

__all__ = ["Command", "LifecycleCommand", "commands"]

commands = Registry(Command, "Command")  # type: Registry[Command]
