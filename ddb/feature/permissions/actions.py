# -*- coding: utf-8 -*-
import os
import shutil
from typing import Optional

from ddb.action import Action
from ddb.action.action import EventBinding
from ddb.config import config
from ddb.event import events
from ddb.utils.file import chmod, FileWalker


class PermissionsAction(Action):
    """
    Update file access permissions based on git index
    """

    @property
    def name(self) -> str:
        return "git:permissions"

    @property
    def event_bindings(self):
        specs = config.data.get('permissions.specs')
        compiled_specs = []
        if specs:
            for spec, mode in specs.items():
                compiled_specs.append((FileWalker.re_compile_patterns(spec), mode))

        def file_found_processor(file: str):
            for spec, mode in compiled_specs:
                if FileWalker.match_any_pattern(file, spec):
                    return (), {"file": file, "mode": mode}
            return None

        def file_generated_processor(source: Optional[str], target: str):
            mode = file_found_processor(target)
            if mode is None and source is not None:
                shutil.copymode(source, target)

            return mode

        return (
            EventBinding(events.file.found, chmod, file_found_processor),
            EventBinding(events.file.generated, chmod, file_generated_processor)
        )

    @property
    def disabled(self) -> bool:
        return os.name == 'nt'
