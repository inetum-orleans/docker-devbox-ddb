import contextlib
import glob
import os
import re
from pathlib import Path

import requests

from ddb.action import Action
from ddb.cache import caches, requests_cache_name
from ddb.config import config
from ddb.event import events
from ddb.utils.file import copy_if_different, write_if_different


def copy_from_url(source, destination, filename=None):
    """
    Copy from an URL source.
    """
    cache = caches.get(requests_cache_name)
    response = cache.get(source)
    if not response:
        response = requests.get(source, allow_redirects=True, timeout=30)
        response.raise_for_status()
        cache.set(source, response)
    if not filename:
        content_disposition = response.headers["content-disposition"]
        filename = re.findall("filename=(.+)", content_disposition)[0]
    target_path = str(Path(destination) / filename)
    if write_if_different(target_path, response.content, "rb", "wb", log_source=source) or config.eject:
        return target_path
    return None


def get_dispatch_directories(dispatch):
    """
    Get dispatch directories from dispatch glob.
    """
    # PTH207: dispatch expressions come from the project configuration and may be absolute,
    # which Path.glob rejects, and Path.glob would also match hidden entries.
    dispatch_directories = []
    if dispatch:
        for dispatch_expr in dispatch:
            if dispatch_expr.startswith("!"):
                matches = glob.glob(dispatch_expr[1:])  # noqa: PTH207
                dirs = [match for match in matches if Path(match).is_dir()]
                for to_remove in dirs:
                    with contextlib.suppress(ValueError):
                        dispatch_directories.remove(to_remove)
            else:
                matches = glob.glob(dispatch_expr)  # noqa: PTH207
                dirs = [match for match in matches if Path(match).is_dir()]
                for to_add in dirs:
                    if to_add not in dispatch_directories:
                        dispatch_directories.append(to_add)

    return dispatch_directories


class CopyAction(Action):
    """
    Copy files from local filesystem or URL to one of many directories.
    """

    @property
    def name(self) -> str:
        return "copy:copy"

    @property
    def event_bindings(self):
        return events.phase.configure

    @staticmethod
    def execute():
        """
        Execute action.
        """
        specs = config.data.get("copy.specs")
        if not specs:
            return

        generated_events = []

        for spec in specs:
            source = spec["source"]
            destination = spec.get("destination")

            dispatch = spec.get("dispatch")
            dispatch_directories = get_dispatch_directories(dispatch)

            if not dispatch_directories:
                dispatch_directories = [""]

            for dispatch_directory in dispatch_directories:
                if destination:
                    file_destination = os.path.relpath(Path(dispatch_directory) / destination)
                    Path(file_destination).mkdir(parents=True, exist_ok=True)
                else:
                    file_destination = os.path.relpath(dispatch_directory)

                for event_source, event_target in CopyAction._copy_from_spec(file_destination, source, spec):
                    generated_events.append((event_source, event_target))

        for event_source, event_target in generated_events:
            events.file.generated(source=event_source, target=event_target)

    @staticmethod
    def _copy_from_spec(destination, source, spec):
        if source.startswith(("http://", "https://")):
            target_path = copy_from_url(source, destination, spec.get("filename"))
            if target_path:
                yield None, target_path
        elif Path(source).exists() and Path(source).is_file():
            filename = spec.get("filename", Path(source).name)
            target_path = str(Path(destination) / filename)
            if copy_if_different(source, target_path, "rb", "wb", log=True) or config.eject:
                yield source, target_path
        else:
            if Path(source).is_dir():
                source = source + "/*"
            # PTH207: sources come from the project configuration, see get_dispatch_directories.
            for file in glob.glob(source):  # noqa: PTH207
                target_path = str(Path(destination) / Path(file).name)
                if copy_if_different(file, target_path, "rb", "wb", log=True) or config.eject:
                    yield file, target_path
