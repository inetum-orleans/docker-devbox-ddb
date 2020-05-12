# -*- coding: utf-8 -*-
import os
from glob import glob

from ddb.action import Action
from ddb.config import config
from ddb.event import events
from ddb.utils.file import chmod


class PermissionsAction(Action):
    """
    Update file access permissions based on git index
    """

    @property
    def name(self) -> str:
        return "git:permissions"

    @property
    def event_bindings(self):
        return events.phase.configure

    @property
    def disabled(self) -> bool:
        return os.name == 'nt'

    @staticmethod
    def execute():
        """
        Execute the action
        :return:
        """
        specs = config.data.get('permissions.specs')
        if specs:
            for spec, mode in specs.items():
                for file in glob(spec, recursive=True):
                    chmod(file, mode)
