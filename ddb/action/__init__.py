# -*- coding: utf-8 -*-
from .action import Action
from ..registry import Registry

actions = Registry(Action, "Action")  # type: Registry[Action]
