# -*- coding: utf-8 -*-
from typing import Iterable

from ddb.action import Action
from ddb.event import events
from ddb.feature import Feature


class Custom2Feature(Feature):
    """
    Custom Feature
    """

    @property
    def name(self) -> str:
        return "custom2"

    @property
    def actions(self) -> Iterable[Action]:
        return (
            Custom2Action(),
        )


class Custom2Action(Action):
    @property
    def event_bindings(self):
        return events.phase.configure

    @property
    def name(self):
        return "custom2_action"

    def execute(self):
        with open("test2", "w") as f:
            f.write("Custom2Action")
