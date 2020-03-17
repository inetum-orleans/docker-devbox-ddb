# -*- coding: utf-8 -*-
import fnmatch
import glob
import os
import re
import shutil

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


class CopyToBuildContextAction(Action):
    """
    Copy specified files to service build context
    """

    @property
    def name(self) -> str:
        return "docker:copy-to-build-context"

    @property
    def event_name(self) -> str:
        return "phase:configure"

    @property
    def order(self) -> int:
        return -128

    def execute(self, *args, **kwargs):
        copy_to_context_build = config.data.get("docker.copy_to_build_context")
        if not copy_to_context_build:
            return

        directory = config.data.get("docker.directory")
        if not os.path.isdir(directory):
            return

        service_directories = [os.path.join(directory, o) for o in os.listdir(directory)
                               if os.path.isdir(os.path.join(directory, o)) and
                               not o.startswith(".")]

        for copy_spec in copy_to_context_build:
            source = copy_spec['source']
            destination = copy_spec.get('destination')
            service = copy_spec.get('service')

            for service_directory in service_directories:
                if destination:
                    file_destination = os.path.join(service_directory, destination)
                    os.makedirs(file_destination, exist_ok=True)
                else:
                    file_destination = service_directory

                if not service \
                        or service_directory == service \
                        or fnmatch.fnmatch(service_directory, service):
                    if source.startswith('http://') or source.startswith('https://'):
                        copy_from_url(source, file_destination, copy_spec.get('filename'))
                    elif os.path.exists(source):
                        filename = copy_spec.get('filename', os.path.basename(source))
                        target_path = os.path.join(file_destination, filename)
                        shutil.copy(source, target_path)
                    else:
                        for file in glob.glob(source):
                            target_path = os.path.join(file_destination, os.path.basename(file))
                            shutil.copy(file, target_path)
