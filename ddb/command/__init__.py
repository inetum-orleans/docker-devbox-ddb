# -*- coding: utf-8 -*-
from .command import LifecycleCommand, Command
from ..registry import Registry

commands = Registry(Command, "Command")  # type: Registry[Command]
