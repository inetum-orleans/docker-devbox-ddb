# -*- coding: utf-8 -*-
import os
import shutil
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.error import HTTPError

import requests
from progress.bar import IncrementalBar

from ddb import __version__
from ddb.action import Action
from ddb.config import config
from ddb.event import events
from ddb.utils.table_display import get_table_display


def get_latest_release_version(github_repository: str):
    """
    Retrieve latest release version from GitHub API
    :param github_repository github repository to check
    :return: Version from tag_name retrieved from GitHub API
    """
    response = requests.get('https://api.github.com/repos/{}/releases/latest'.format(github_repository))
    try:
        response.raise_for_status()
        tag_name = response.json().get('tag_name')
        if tag_name and tag_name.startswith('v'):
            tag_name = tag_name[1:]
        return tag_name
    except HTTPError:  # pylint:disable=bare-except
        return None


def get_current_version():
    """
    Get the current version
    :return:
    """
    return __version__


def print_version(silent=False):
    """
    Print the version and informations.
    :return:
    """
    if silent:
        print(get_current_version())
        return

    version_title = 'ddb ' + get_current_version()
    version_content = []

    github_repository = config.data.get('selfupdate.github_repository')

    last_release = get_latest_release_version(github_repository)

    if last_release and get_current_version() < last_release:
        version_content.append(_build_update_header(last_release))
        version_content.append(_build_update_details(github_repository, last_release))
    version_content.append([
        'Please report any bug or feature request at',
        'https://github.com/gfi-centre-ouest/docker-devbox-ddb/issues'
    ])
    print(get_table_display(version_title, version_content))


def check_for_update(output=False, details=False):
    """
    Check if a new version is available on github.
    :param output: if True, new version information will be displayed.
    :param details: if True, will display more details.
    :return: True if an update is available.
    """
    github_repository = config.data.get('selfupdate.github_repository')

    last_release = get_latest_release_version(github_repository)

    if last_release and get_current_version() < last_release:
        if output:
            header = _build_update_header(last_release)
            if details:
                row = _build_update_details(github_repository, last_release)
                print(get_table_display(header, [row]))
            else:
                for row in header:
                    print(row)
        return True
    return False


def _build_update_header(last_release):
    return ['A new version is available: {}'.format(last_release)]


def _build_update_details(github_repository, last_release):
    row = []
    if is_binary():
        row.append('run "ddb self-update" command to update.')
    row.extend((
        'For more information, check the following links:',
        'https://github.com/{}/releases/tag/{}'.format(github_repository, last_release),
        'https://github.com/{}/releases/tag/{}/CHANGELOG.md'.format(github_repository, last_release),
    ))
    return row


def is_binary():
    """
    Check if current process is binary.
    :return:
    """
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')


def get_binary_path():
    """
    Get the binary path
    :return:
    """
    return sys.argv[0]


def get_binary_destination_path(binary_path: str):
    """
    Get binary path destination
    :param binary_path:
    :return:
    """
    if binary_path.endswith('.py') \
            and Path(binary_path).read_text().startswith("#!/usr/bin/env python"):
        # Avoid removing main source file when running on development.
        binary_path = binary_path[:-3] + ".bin"
    return binary_path


class SelfUpdateAction(Action):
    """
    Self update ddb if a newer version is available.
    """

    @property
    def name(self) -> str:
        return "selfupdate:update"

    @property
    def event_bindings(self):
        return events.phase.selfupdate

    def execute(self):
        """
        Execute action
        """
        github_repository = config.data.get('selfupdate.github_repository')

        if not is_binary():
            print('ddb is running from a package mode than doesn\'t support self-update.')
            print(
                'You can download binary package supporting it ' +
                'from github: https://github.com/{}/releases'.format(github_repository)
            )
            return

        last_release = get_latest_release_version(github_repository)

        if not check_for_update(True):
            print('ddb is already up to date.')
            if not config.args.force:
                return

        self.self_update_binary(github_repository, last_release)

    @staticmethod
    def self_update_binary(github_repository, version):
        """
        Self update the ddb binary
        :param github_repository:
        :param version:
        :return:
        """
        binary_path = get_binary_path()

        if not os.access(binary_path, os.W_OK):
            raise PermissionError("You don't have permission to write on ddb binary file. ({})".format(sys.argv[0]))

        remote_filename = 'ddb.exe' if os.name == 'nt' else 'ddb'
        url = 'https://github.com/{}/releases/download/v{}/{}'.format(github_repository, version, remote_filename)

        progress_bar = None
        with requests.get(url, stream=True) as response:
            response.raise_for_status()

            with NamedTemporaryFile() as tmp:
                if not progress_bar:
                    content_length = int(response.headers['content-length'])
                    progress_bar = IncrementalBar('Downloading', max=content_length)

                for chunk in response.iter_content(32 * 1024):
                    progress_bar.next(len(chunk))  # pylint:disable=not-callable
                    tmp.write(chunk)
                tmp.flush()

                binary_path = get_binary_destination_path(binary_path)
                shutil.copyfile(tmp.name, binary_path)

            progress_bar.finish()

        print("ddb has been updated.")
