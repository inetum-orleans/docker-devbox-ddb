from collections.abc import Iterable

from ...action import Action
from ...action.action import EventBinding
from ...binary import Binary, binaries
from ...config import config
from ...event import events


class RunAction(Action):
    """
    Run a binary.
    """

    @property
    def event_bindings(self):
        return (events.phase.run, EventBinding(events.run.run, self.run))

    @property
    def name(self) -> str:
        return "run:run"

    @staticmethod
    def execute():
        """
        Execute the action defined by argument "name".
        """
        if hasattr(config.args, "name"):
            name = config.args.name
            events.run.run(name=name)

    @staticmethod
    def run(name: str, *args):
        """
        Execute the action.
        """
        if not args:
            args = tuple(config.unknown_args)

        binary_set = binaries.get(name)
        binary = None
        if binary_set:
            binary = RunAction.select_binary(binary_set, *args)

        if binary:
            binary.before_run()
            events.run.command(binary.command(*args), system_path=False)
        else:
            events.run.command([name, *args], system_path=True)

    @staticmethod
    def select_binary(binary_set: Iterable[Binary], *args) -> Binary | None:
        """
        Select effective binary between many binaries.
        """
        ordered_binary = sorted(binary_set)  # type: ignore[type-var]
        for binary in ordered_binary:
            if binary.should_run(*args):
                return binary
        return None
