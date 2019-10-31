# -*- coding: utf-8 -*-
import os
from os.path import exists
from pathlib import Path
from typing import Callable, Any

import yaml
from deepmerge import always_merger
from dotty_dict import dotty
from marshmallow import Schema


def get_default_config_paths(env_prefix):
    """
    Get configuration paths
    """
    project_home = os.environ.get(env_prefix + '_PROJECT_HOME', os.getcwd())
    home = os.environ.get(env_prefix + '_HOME', os.path.join(str(Path.home()), '.docker-devbox'))
    ddb_home = os.environ.get(env_prefix + '_DDB_HOME', os.path.join(home, 'ddb'))

    return ddb_home, home, project_home


class Config:
    """
    Configuration
    """

    def __init__(self, config_paths=None, env_prefix='DDB', filenames=('ddb', 'ddb.local'),
                 extensions=('yml', 'yaml')):
        self.env_prefix = env_prefix
        self.filenames = filenames
        self.extensions = extensions
        self.data = dotty()
        self.config_paths = config_paths if config_paths else get_default_config_paths(env_prefix)

    def clear(self):
        """
        Remove all configuration data.
        """
        self.data.clear()

    def load(self, env_key='env'):
        """
        Load configuration data. Variable in 'env_key' key will be placed loaded as environment variables.
        """
        self.data.clear()
        loaded_data = {}

        for config_path in self.config_paths:
            for basename in self.filenames:
                for ext in self.extensions:
                    file = os.path.join(config_path, basename + '.' + ext)
                    if exists(file):
                        with open(file, 'rb') as stream:
                            file_data = yaml.load(stream, Loader=yaml.FullLoader)
                            loaded_data = always_merger.merge(loaded_data, file_data)

        if env_key in loaded_data:
            env = loaded_data.pop(env_key)
            if env:
                for (name, value) in env.items():
                    os.environ[name] = value

        loaded_data = self.apply_environment_variables(loaded_data)
        self.data.update(loaded_data)

    def sanitize_and_validate(self, schema: Schema, key: str, auto_configure: Callable[[dict], Any] = None):
        """
        Sanitize and validate using given schema part of the configuration given by configuration key.
        """

        raw_feature_config = self.data.get(key)

        if not raw_feature_config:
            raw_feature_config = {}
        feature_config = schema.dump(raw_feature_config)

        feature_config = self.apply_environment_variables(feature_config, self.env_prefix + "_" + key)
        feature_config = schema.dump(feature_config)

        if auto_configure:
            auto_configure(feature_config)

        feature_config = schema.load(feature_config)
        self.data[key] = feature_config

    def apply_environment_variables(self, data, prefix=None):
        """
        Apply environment variables to configuration.
        """
        if not prefix:
            prefix = self.env_prefix
        prefix = prefix.upper()

        environ_value = os.environ.get(prefix)
        if environ_value:
            return environ_value

        if isinstance(data, dict):
            for (name, value) in data.items():
                key_prefix = prefix + "_" + name
                key_prefix = key_prefix.upper()

                data[name] = self.apply_environment_variables(value, key_prefix)
        if isinstance(data, list):
            i = 0
            for value in data:
                replace_prefix = prefix + "[" + str(i) + "]"
                replace_prefix = replace_prefix.upper()

                environ_value = os.environ.get(replace_prefix)
                if environ_value:
                    data[i] = self.apply_environment_variables(value, replace_prefix)

                i += 1

        return data
