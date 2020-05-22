# -*- coding: utf-8 -*-
import os
from typing import Optional

from wcmatch.glob import globmatch, GLOBSTAR

from ddb.action import Action
from ddb.action.action import EventBinding
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
        def file_found_processor(file: str):
            specs = config.data.get('permissions.specs')
            if specs:
                for spec, mode in specs.items():
                    if globmatch(file, spec, flags=GLOBSTAR):
                        return (), {"file": file, "mode": mode}
            return None

        def file_generated_processor(source: Optional[str], target: str):
            return file_found_processor(target)

        return (
            EventBinding(events.file.found, chmod, file_found_processor),
            EventBinding(events.file.generated, chmod, file_generated_processor)
        )

    @property
    def disabled(self) -> bool:
        return os.name == 'nt'
