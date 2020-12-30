# -*- coding: utf-8 -*-
import os
import subprocess
from typing import Optional

from ...context import context
from ...action import Action
from ...action.action import EventBinding
from ...binary import binaries
from ...binary.binary import Binary
from ...config import config
from ...event import events


class RunAction(Action):
    """
    Run a binary
    """

    @property
    def event_bindings(self):
        return (
            events.phase.run,
            EventBinding(events.run.run, self.run)
        )

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
        Execute the action
        """
        if not args:
            args = config.unknown_args

        binary = RunAction.get_binary(name)
        if binary.pre_execute():
            print(subprocess.list2cmdline(binary.command(*args)))
        else:
            context.log.error("An error occurred in pre-execution controls of the binary")

    @staticmethod
    def get_binary(name: str) -> Binary:
        """
        Retrieve a binary from his name
        :param name:
        :return:
        """
        matching_binaries = [binary for binary in binaries.all() if binary.name.endswith(name)]

        if len(matching_binaries) == 0:
            raise ValueError(" binary named \"" + name + "\" is not registered")

        binary: Optional[Binary] = None
        for tmp_binary in matching_binaries:
            if tmp_binary.in_folder is not None:
                binary_folder = os.path.join(config.data['core']['path']['project_home'], tmp_binary.in_folder)
                if config.cwd.startswith(binary_folder):
                    binary = tmp_binary
            elif tmp_binary.in_folder is None and binary is None:
                binary = tmp_binary

        if binary is None:
            raise ValueError(" binary named name \"" + name + "\" is not available in your current working directory")

        return binary
