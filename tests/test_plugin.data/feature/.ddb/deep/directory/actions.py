from ddb.action import Action
from ddb.event import events


class CustomAction(Action):
    @property
    def event_bindings(self):
        return events.phase.configure

    @property
    def name(self):
        return "custom_action3"

    def execute(self):
        with open("test3", "w") as f:
            f.write("Custom3Action")
