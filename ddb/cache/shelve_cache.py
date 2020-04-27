# -*- coding: utf-8 -*-
import os
import shelve
import tempfile

from .cache import Cache
from ..config import config


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

        self._shelf = shelve.open(os.path.join(path, self._namespace))

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
