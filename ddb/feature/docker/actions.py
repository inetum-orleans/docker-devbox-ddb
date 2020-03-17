# -*- coding: utf-8 -*-
import fnmatch
import glob
import os
import shutil

from ddb.action import Action
from ddb.config import config


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

            for file in glob.glob(source):
                for service_directory in service_directories:
                    if not service \
                            or service_directory == service \
                            or fnmatch.fnmatch(service_directory, service):
                        if destination:
                            file_destination = os.path.join(service_directory, destination)
                            os.makedirs(file_destination, exist_ok=True)
                        else:
                            file_destination = service_directory
                        file_destination = os.path.join(file_destination, os.path.basename(file))
                        shutil.copy(file, file_destination)
