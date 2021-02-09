# -*- coding: utf-8 -*-
import os
from argparse import Namespace
from collections import namedtuple
from copy import deepcopy
from os.path import exists
from pathlib import Path
from typing import Union, Iterable, Dict

import yaml

from ddb.config.merger import config_merger
from ddb.config.migrations import MigrationsDotty

ConfigPaths = namedtuple('ConfigPaths', ['ddb_home', 'home', 'project_home'])


def configuration_file(path: str, filenames: Iterable[str], extensions: Iterable[str]):
    """
    Find configuration file for given path and possible filename/extensions
    """
    if path:
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

    project_home = os.path.abspath(project_home)

    home = os.environ.get(env_prefix + '_HOME', os.path.join(str(Path.home()), '.docker-devbox'))
    ddb_home = os.environ.get(env_prefix + '_DDB_HOME', os.path.join(home, 'ddb'))

    return ConfigPaths(ddb_home=ddb_home, home=home, project_home=project_home)


class Config:  # pylint:disable=too-many-instance-attributes
    """
    Configuration
    """
    # Static default/overrides values for configuration, can be modified from code mainly for tests purpose
    defaults = None
    overrides = lambda config: config

    def __init__(self,
                 paths: Union[ConfigPaths, None] = None,
                 env_prefix='DDB',
                 env_override_prefix='DDB_OVERRIDE',
                 filenames=('ddb', 'ddb.local'),
                 extensions=('yml', 'yaml'),
                 cwd=None,
                 args=None,
                 unknown_args=None):
        self.env_prefix = env_prefix
        self.env_override_prefix = env_override_prefix
        self.filenames = filenames
        self.extensions = extensions
        self.env_additions = {}
        self.data = MigrationsDotty()
        self.paths = paths if paths else get_default_config_paths(env_prefix, filenames, extensions)
        self.cwd = cwd
        self.args = args if args else Namespace()
        self.unknown_args = unknown_args if unknown_args else []
        self.env_key = 'env'

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

    @property
    def project_configuration_file(self):
        """
        Retrieve the project configuration file.
        """
        return configuration_file(self.paths.project_home, self.filenames, self.extensions)

    @property
    def project_cwd(self):
        """
        Retrieve the current working directory, relative to project_home.
        :return:
        """
        if self.paths.project_home and self.cwd:
            return os.path.relpath(self.cwd, self.paths.project_home)
        return None

    @property
    def eject(self):
        """
        Check if command line is running configure command with --eject flag.
        :return:
        """
        return 'command' in self.args and self.args.command == 'configure' and \
               'eject' in self.args and self.args.eject

    @property
    def clear_cache(self):
        """
        Should cache be cleared on load
        """
        if 'clear_cache' in self.args:
            return self.args.clear_cache
        return False

    @property
    def files(self):
        """
        Possible configuration files to load.
        """
        ret = []
        for path in self.paths:
            if not path:
                continue
            for basename in self.filenames:
                for ext in self.extensions:
                    if basename.endswith('.' + ext) and os.path.exists(os.path.join(path, basename)):
                        file = os.path.join(path, basename)
                    else:
                        file = os.path.join(path, basename + '.' + ext)
                    ret.append(file)
        return ret

    def read(self, defaults=None, files=None):
        """
        Read configuration data from files.
        """
        if defaults is None:
            loaded_data = {}
        else:
            loaded_data = dict(defaults)

        if files is None:
            files = self.files

        found_files = {}

        for file in files:
            if exists(file):
                with open(file, 'rb') as stream:
                    file_data = yaml.safe_load(stream)
                    found_files[file] = self.apply_environ_overrides(deepcopy(file_data))
                    if file_data:
                        loaded_data = config_merger.merge(loaded_data, file_data)

        if Config.overrides:  # pylint:disable=using-constant-test
            Config.overrides(loaded_data)

        return self.apply_environ_overrides(loaded_data), found_files

    def load_from_data(self, data: Dict):
        """
        Load configuration data from readen files.
        """
        merged_data = config_merger.merge(dict(self.data.raw()), data)
        self.data = MigrationsDotty(merged_data)

        if self.env_key in self.data:
            env = self.data.pop(self.env_key)
            if env:
                for (name, value) in env.items():
                    os.environ[name] = value

    def load(self, defaults=None, files=None):
        """
        Load configuration data from files. Variable in 'env_key' key will be placed loaded as environment variables.
        """
        defaults_to_apply = {} if Config.defaults is None else dict(Config.defaults)
        if defaults:
            # Config.defaults should have the priority over given defaults.
            defaults_to_apply = config_merger.merge(defaults, defaults_to_apply)
        read_data, _ = self.read(defaults_to_apply, files)
        self.load_from_data(read_data)

    def apply_environ_overrides(self, data, prefix=None):
        """
        Apply environment variables to configuration.
        """
        if not prefix:
            prefix = self.env_override_prefix
        prefix = prefix.upper()

        environ_value = os.environ.get(prefix)
        if environ_value:
            if environ_value.lower() == str(True):
                environ_value = True
            elif environ_value.lower() == str(False):
                environ_value = False
            elif environ_value.isdigit():
                environ_value = int(environ_value)
            if isinstance(data, bool):
                environ_value = bool(environ_value)
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
