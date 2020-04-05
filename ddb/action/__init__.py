# -*- coding: utf-8 -*-
from .action import Action, InitializableAction
from ..registry import Registry

actions = Registry(Action, "Action")  # type: Registry[Action]
