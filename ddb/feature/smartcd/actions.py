from subprocess import run, PIPE, CalledProcessError
from typing import Union, Iterable, Callable

from ddb.action.action import EventBinding, InitializableAction
from ddb.command import commands
from ddb.event import events
from ddb.utils.file import write_if_different


def is_smartcd_installed():
    """
    Run smartcd command to check if it"s installed.
    """

    try:
        run(["/usr/bin/env", "bash", "-ic", "smartcd", "--help"],
            check=True,
            stdout=PIPE, stderr=PIPE)
        return True
    except CalledProcessError:
        return False


class SmartcdAction(InitializableAction):
    """
    Generate bash_enter/bash_leave files if smartcd is installed
    """

    @property
    def event_bindings(self) -> Union[Iterable[Union[Callable, str, EventBinding]], Union[Callable, str, EventBinding]]:
        return events.phase.configure

    @property
    def name(self) -> str:
        return "smartcd:generate"

    @staticmethod
    def execute():
        """
        Write .bash_enter/.bash_leave files.
        :return:
        """
        if not commands.has("activate") and not commands.has("deactivate"):
            return
        if not is_smartcd_installed():
            return

        if write_if_different(".bash_enter", "echo [smartcd] Activate\n$(ddb activate)\n"):
            events.file.generated(source=None, target=".bash_enter")

        if write_if_different(".bash_leave", "echo [smartcd] Deactivate\n$(ddb deactivate)\n"):
            events.file.generated(source=None, target=".bash_leave")
