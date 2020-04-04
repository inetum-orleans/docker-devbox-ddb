# -*- coding: utf-8 -*-
import glob
import os
import re
import shutil
from typing import Iterable, Union, Callable

import requests

from ddb.action import Action
from ddb.cache import caches, _requests_cache_name
from ddb.config import config


def copy_from_url(source, destination, filename=None):
    """
    Copy from an URL source.
    """
    cache = caches.get(_requests_cache_name)
    response = cache.get(source)
    if not response:
        response = requests.get(source, allow_redirects=True)
        response.raise_for_status()
        cache.set(source, response)
    if not filename:
        content_disposition = response.headers['content-disposition']
        filename = re.findall("filename=(.+)", content_disposition)[0]
    target_path = os.path.join(destination, filename)
    with open(target_path, 'wb') as output_file:
        output_file.write(response.content)


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
    def event_bindings(self) -> Union[str, Iterable[Union[Iterable[str], Callable]]]:
        return "phase:init"

    def execute(self, *args, **kwargs):
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
                    file_destination = os.path.join(dispatch_directory, destination)
                    os.makedirs(file_destination, exist_ok=True)
                else:
                    file_destination = dispatch_directory

                if source.startswith('http://') or source.startswith('https://'):
                    copy_from_url(source, file_destination, spec.get('filename'))
                elif os.path.exists(source):
                    filename = spec.get('filename', os.path.basename(source))
                    target_path = os.path.join(file_destination, filename)
                    shutil.copy(source, target_path)
                else:
                    for file in glob.glob(source):
                        target_path = os.path.join(file_destination, os.path.basename(file))
                        shutil.copy(file, target_path)
