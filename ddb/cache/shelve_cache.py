# -*- coding: utf-8 -*-
import os
import shelve
import tempfile

from .cache import Cache
from ..config import config

import dbm

# Easy fix for https://github.com/inetum-orleans/docker-devbox-ddb/issues/49
# pylint:disable=protected-access
_dbm_names = dbm._names = ['dbm.gnu', 'dbm.ndbm', 'dbm.dumb']
if 'dbm.dumb' in _dbm_names:
    # Let's make dbm.dumb the preferred implementation
    _dbm_names.remove('dbm.dumb')
    _dbm_names.insert(0, 'dbm.dumb')
    dbm._names = _dbm_names


class ShelveCache(Cache):
    """
    A cache implementation relying of shelve module.
    """

    def __init__(self, namespace: str):
        super().__init__(namespace)

        if config.paths.home:
            path = os.path.join(config.paths.home, "cache")
        else:
            path = os.path.join(tempfile.gettempdir(), "ddb", "cache")
        os.makedirs(path, exist_ok=True)

        filename = os.path.join(path, self._namespace)
        if config.clear_cache and os.path.exists(filename):
            os.remove(filename)
        try:
            self._shelf = shelve.open(filename)
        except Exception as open_error:  # pylint:disable=broad-except
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                    self._shelf = shelve.open(filename)
                except Exception as fallback_error:  # pylint:disable=broad-except
                    raise open_error from fallback_error
            else:
                raise open_error
        if config.clear_cache:
            self._shelf.clear()

    def close(self):
        self._shelf.close()

    def flush(self):
        self._shelf.sync()

    def get(self, key: str, default=None):
        return self._shelf.get(key, default)

    def keys(self):
        return self._shelf.keys()

    def set(self, key: str, data):
        self._shelf[key] = data

    def pop(self, key: str):
        return self._shelf.pop(key)

    def clear(self):
        self._shelf.clear()

    def __contains__(self, key):
        return self._shelf.__contains__(key)
