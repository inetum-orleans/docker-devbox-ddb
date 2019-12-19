# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod


class Cache(ABC):
    """
    Cache interface
    """

    def __init__(self, namespace: str):
        self._namespace = namespace

    @abstractmethod
    def get(self, key: str, default=None):
        """
        Get a cache entry value
        """

    @abstractmethod
    def set(self, key: str, data):
        """
        Set a cache entry value
        """

    @abstractmethod
    def clear(self):
        """
        Remove all cache entries.
        """

    def close(self):
        """
        Close the cache access.
        """

    def flush(self):
        """
        Synchronize the cache with persistent system.
        """
