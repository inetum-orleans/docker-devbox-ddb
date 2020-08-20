# -*- coding: utf-8 -*-
import os
from argparse import Namespace
from collections import namedtuple
from os.path import exists
from pathlib import Path
from typing import Callable, Any, Union, Iterable

import yaml
from deepmerge import always_merger
from dotty_dict import dotty, Dotty
from marshmallow import Schema

ConfigPaths = namedtuple('ConfigPaths', ['ddb_home', 'home', 'project_home'])


def configuration_file(path: str, filenames: Iterable[str], extensions: Iterable[str]):
    """
    Find configuration file for given path and possible filename/extensions
    """
    for basename in filenames:
        for ext in extensions:
            file = os.path.join(path, basename + '.' + ext)
            if exists(file):
                return file
    return None


def get_default_config_paths(env_prefix, filenames, extensions) -> ConfigPaths:
    """
    Get configuration paths
    """
    if os.environ.get(env_prefix + '_PROJECT_HOME'):
        project_home = os.environ.get(env_prefix + '_PROJECT_HOME')
    else:
        project_home_candidate = os.getcwd()
        while not configuration_file(project_home_candidate, filenames, extensions):
            project_home_candidate_parent = str(Path(project_home_candidate).parent)
            if project_home_candidate_parent == project_home_candidate:
                project_home_candidate = os.getcwd()
                break
            project_home_candidate = project_home_candidate_parent
        project_home = project_home_candidate

    home = os.environ.get(env_prefix + '_HOME', os.path.join(str(Path.home()), '.docker-devbox'))
    ddb_home = os.environ.get(env_prefix + '_DDB_HOME', os.path.join(home, 'ddb'))

    return ConfigPaths(ddb_home=ddb_home, home=home, project_home=project_home)


class Config:  # pylint:disable=too-many-instance-attributes
    """
    Configuration
    """
    # Static default values for configuration, can be modified from code mainly for tests purpose
    defaults = None

    def __init__(self,
                 paths: Union[ConfigPaths, None] = None,
                 env_prefix='DDB',
                 env_override_prefix='DDB_OVERRIDE',
                 filenames=('ddb', 'ddb.local'),
                 extensions=('yml', 'yaml')):
        self.env_prefix = env_prefix
        self.env_override_prefix = env_override_prefix
        self.filenames = filenames
        self.extensions = extensions
        self.env_additions = {}
        self.data = dotty()
        self.paths = paths if paths else get_default_config_paths(env_prefix, filenames, extensions)
        self.args = Namespace()
        self.unknown_args = []

    def reset(self, *args, **kwargs):
        """
        Reset the configuration object, while keeping configured paths.
        """
        self.__init__(*args, paths=self.paths, **kwargs)

    def clear(self):
        """
        Remove all configuration data.
        """
        self.data.clear()
        self.env_additions.clear()

    def load(self, env_key='env'):
        """
        Load configuration data. Variable in 'env_key' key will be placed loaded as environment variables.
        """
        loaded_data = {} if Config.defaults is None else dict(Config.defaults)

        for path in self.paths:
            if not path:
                continue
            for basename in self.filenames:
                for ext in self.extensions:
                    file = os.path.join(path, basename + '.' + ext)
                    if exists(file):
                        with open(file, 'rb') as stream:
                            file_data = yaml.load(stream, Loader=yaml.FullLoader)
                            if file_data:
                                loaded_data = always_merger.merge(loaded_data, file_data)

        if env_key in loaded_data:
            env = loaded_data.pop(env_key)
            if env:
                for (name, value) in env.items():
                    os.environ[name] = value

        loaded_data = self.apply_environ_overrides(loaded_data)
        self.data = dotty(always_merger.merge(self.data, loaded_data))

    def sanitize_and_validate(self, schema: Schema, key: str, auto_configure: Callable[[Dotty], Any] = None):
        """
        Sanitize and validate using given schema part of the configuration given by configuration key.
        """

        raw_feature_config = self.data.get(key)

        if not raw_feature_config:
            raw_feature_config = {}
        feature_config = schema.dump(raw_feature_config)

        feature_config = self.apply_environ_overrides(feature_config, self.env_override_prefix + "_" + key)
        feature_config = schema.dump(feature_config)

        if auto_configure:
            auto_configure(dotty(feature_config))

        feature_config = schema.load(feature_config)
        self.data[key] = feature_config

    def apply_environ_overrides(self, data, prefix=None):
        """
        Apply environment variables to configuration.
        """
        if not prefix:
            prefix = self.env_override_prefix
        prefix = prefix.upper()

        environ_value = os.environ.get(prefix)
        if environ_value:
            return environ_value

        if isinstance(data, dict):
            for (name, value) in data.items():
                key_prefix = prefix + "_" + name
                key_prefix = key_prefix.upper()

                data[name] = self.apply_environ_overrides(value, key_prefix)
        if isinstance(data, list):
            i = 0
            for value in data:
                replace_prefix = prefix + "[" + str(i) + "]"
                replace_prefix = replace_prefix.upper()

                environ_value = os.environ.get(replace_prefix)
                if environ_value:
                    data[i] = self.apply_environ_overrides(value, replace_prefix)

                i += 1

        return data
