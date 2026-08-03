from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any


class Cache(ABC):
    """
    Cache interface.
    """

    def __init__(self, namespace: str) -> None:
        self._namespace = namespace

    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a cache entry value.
        """

    @abstractmethod
    def keys(self) -> Iterable[str]:
        """
        Get all cache keys.
        """

    @abstractmethod
    def set(self, key: str, data: Any) -> None:
        """
        Set a cache entry value.
        """

    @abstractmethod
    def pop(self, key: str) -> Any:
        """
        Remove a cache entry.
        """

    @abstractmethod
    def clear(self) -> None:
        """
        Remove all cache entries.
        """

    def close(self) -> None:
        """
        Close the cache access.
        """

    def flush(self) -> None:
        """
        Synchronize the cache with persistent system.
        """

    @abstractmethod
    def __contains__(self, key: str) -> bool:
        """
        Check if key exists.
        """
