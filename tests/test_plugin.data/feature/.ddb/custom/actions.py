from ddb.action import Action
from ddb.event import events


class CustomAction(Action):
    @property
    def event_bindings(self):
        return events.phase.configure

    @property
    def name(self):
        return "custom_action"

    def execute(self):
        with open("test", "w") as f:
            f.write("CustomAction")
