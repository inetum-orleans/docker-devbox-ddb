# -*- coding: utf-8 -*-

from cookiecutter.config import DEFAULT_CONFIG
from cookiecutter.main import cookiecutter

from ddb.action import Action
from ddb.config import config
from ddb.event import events


class CookiecutterAction(Action):
    """
    Download a cookiecutter template.
    """

    @property
    def name(self) -> str:
        return "cookiecutter:download"

    @property
    def event_bindings(self):
        return events.phase.init

    def execute(self):
        """
        Execute action
        """
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
                    # TODO: Generate in a temporary dir to emit file:generated events.
                    self._generate_template(template)
        finally:
            for parameter in config_parameters:
                DEFAULT_CONFIG[parameter] = defaults[parameter]

    @staticmethod
    def _generate_template(template):
        if template['no_input'] is None:
            template['no_input'] = True

        kwargs = {k: v for k, v in template.items() if v is not None}

        return cookiecutter(**kwargs)
