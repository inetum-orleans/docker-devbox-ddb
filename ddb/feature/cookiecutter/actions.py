# -*- coding: utf-8 -*-
import subprocess
from typing import Iterable

from cookiecutter.config import DEFAULT_CONFIG
from cookiecutter.exceptions import VCSNotInstalled, RepositoryNotFound
from cookiecutter.main import cookiecutter
from cookiecutter.repository import is_repo_url
from cookiecutter.vcs import identify_repo, is_vcs_installed

from ddb.action import Action
from ddb.config import config
from ddb.context import context


class ListTagsAction(Action):
    """
    Fetch all tags from cookiecutter templates URLs and save them in context data.
    """

    @property
    def name(self) -> str:
        return "cookiecutter:list-tags"

    @property
    def event_name(self) -> str:
        return "phase:init"

    def execute(self, *args, **kwargs):
        context.data[self.name] = {}

        templates = config.data.get('cookiecutter.templates')
        if templates:
            i = 0
            for template in templates:
                tags = self._list_tags(template['template'])
                if tags is not None:
                    context.data[self.name][i] = tags
                i += 1

    @staticmethod
    def _list_tags(repo_url: str):
        """
        List tags from a repo url
        """
        if not is_repo_url(repo_url):
            return None

        # identify the repo_type
        repo_type, repo_url = identify_repo(repo_url)
        if repo_type != 'git':
            return None

        # check that the appropriate VCS for the repo_type is installed
        if not is_vcs_installed(repo_type):
            msg = "'{0}' is not installed.".format(repo_type)
            raise VCSNotInstalled(msg)

        repo_url = repo_url.rstrip('/')
        try:
            output = subprocess.check_output(
                [repo_type, 'ls-remote', '--tags', '--refs', '--quiet', repo_url]
            )
        except subprocess.CalledProcessError as clone_error:
            output = clone_error.output.decode('utf-8')
            if 'not found' in output.lower():
                raise RepositoryNotFound(
                    'The repository {} could not be found, '
                    'have you made a typo?'.format(repo_url)
                )
            raise

        tags = []
        for line_buffer in output.splitlines():
            line = line_buffer.decode("utf8")

            _, ref = line.split('\t')
            if ref.startswith('refs/tags/'):
                ref = ref[len('refs/tags/'):]
                tags.append(ref)

        return tags


class CookiecutterAction(Action):
    """
    Fetch all tags from git cookiecutter templates.
    """

    @property
    def name(self) -> str:
        return "cookiecutter:download"

    @property
    def event_name(self) -> str:
        return "phase:init"

    @property
    def dependencies(self) -> Iterable[str]:
        return ["cookiecutter:list-tags"]

    def execute(self, *args, **kwargs):
        config_parameters = 'cookiecutters_dir', 'replay_dir', 'default_context'

        defaults = {}
        for parameter in config_parameters:
            defaults[parameter] = DEFAULT_CONFIG[parameter]

        cookiecutter_config = config.data.get('cookiecutter')
        try:
            if cookiecutter_config:
                for parameter in config_parameters:
                    try:
                        DEFAULT_CONFIG[parameter] = cookiecutter_config[parameter]
                    except KeyError:
                        pass

            templates = cookiecutter_config.get('templates')
            if templates:
                for template in templates:
                    self._generate_template(template)
        finally:
            for parameter in config_parameters:
                DEFAULT_CONFIG[parameter] = defaults[parameter]

    @staticmethod
    def _generate_template(template):
        if template['no_input'] is None:
            template['no_input'] = True

        kwargs = {k: v for k, v in template.items() if v is not None}

        cookiecutter(**kwargs)
