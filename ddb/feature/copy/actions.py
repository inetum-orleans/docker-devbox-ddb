# -*- coding: utf-8 -*-
import glob
import os
import re

import requests

from ddb.action import Action
from ddb.cache import caches, requests_cache_name
from ddb.config import config
from ddb.event import events
from ddb.utils.file import write_if_different, copy_if_different


def copy_from_url(source, destination, filename=None):
    """
    Copy from an URL source.
    """
    cache = caches.get(requests_cache_name)
    response = cache.get(source)
    if not response:
        response = requests.get(source, allow_redirects=True)
        response.raise_for_status()
        cache.set(source, response)
    if not filename:
        content_disposition = response.headers['content-disposition']
        filename = re.findall("filename=(.+)", content_disposition)[0]
    target_path = os.path.join(destination, filename)
    write_if_different(target_path, response.content, 'rb', 'wb', log_source=source)
    return target_path


def get_dispatch_directories(dispatch):
    """
    Get dispatch directories from dispatch glob
    """
    dispatch_directories = []

    for dispatch_expr in dispatch:
        if dispatch_expr.startswith("!"):
            matches = glob.glob(dispatch_expr[1:])
            dirs = [match for match in matches if os.path.isdir(match)]
            for to_remove in dirs:
                try:
                    dispatch_directories.remove(to_remove)
                except ValueError:
                    pass
        else:
            matches = glob.glob(dispatch_expr)
            dirs = [match for match in matches if os.path.isdir(match)]
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
        return events.phase.init

    @staticmethod
    def execute():
        """
        Execute action
        """
        specs = config.data.get("copy.specs")
        if not specs:
            return

        for spec in specs:
            source = spec['source']
            destination = spec.get('destination')

            dispatch = spec.get('dispatch')
            dispatch_directories = get_dispatch_directories(dispatch)

            if not dispatch_directories:
                dispatch_directories = [os.path.dirname(destination)]

            for dispatch_directory in dispatch_directories:
                if destination:
                    file_destination = os.path.relpath(os.path.join(dispatch_directory, destination))
                    os.makedirs(file_destination, exist_ok=True)
                else:
                    file_destination = os.path.relpath(dispatch_directory)

                if source.startswith('http://') or source.startswith('https://'):
                    copy_from_url(source, file_destination, spec.get('filename'))
                elif os.path.exists(source):
                    filename = spec.get('filename', os.path.basename(source))
                    target_path = os.path.join(file_destination, filename)
                    copy_if_different(source, target_path, 'rb', 'wb', log=True)
                else:
                    for file in glob.glob(source):
                        target_path = os.path.join(file_destination, os.path.basename(file))
                        copy_if_different(file, target_path, 'rb', 'wb', log=True)
