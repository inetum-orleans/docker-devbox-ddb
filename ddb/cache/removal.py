from collections import defaultdict
from collections.abc import Iterable, Iterator
from typing import Any

from ddb.cache import caches, register_project_cache


class RemovalCacheSupport:
    """
    Handle a cache to support removal of previously generated resources when they are not linked to the current
    configuration anymore.
    """

    def __init__(self, cache_name: str, keys: Iterable[str]) -> None:
        self.cache_name = cache_name
        self.keys = set(keys)
        self.type = set

        self.cached: defaultdict[str, set[Any]] = defaultdict(self.type)
        self.previous: defaultdict[str, set[Any]] = defaultdict(self.type)
        self.current: defaultdict[str, set[Any]] = defaultdict(self.type)

        register_project_cache(self.cache_name)

    def prepare(self) -> None:
        """
        Snapshot the current entries, before processing extra-services configuration.
        """
        cache = caches.get(self.cache_name)

        for key in self.keys:
            self.cached[key] = cache.get(key, self.type())
            self.previous[key] = self.type(self.cached[key])
            self.current[key] = self.type()

    def set_current_value(self, key: str, value: Any) -> None:
        """
        Set current value for given key.
        """
        if key not in self.keys:
            msg = f"Given key '{key}' doesn't match any of the supported key {self.keys}"
            raise ValueError(msg)
        self.cached[key].add(value)
        self.current[key].add(value)

    def get_removed(self) -> Iterator[tuple[str, Any]]:
        """
        Generate the (key, value) entries to remove, after processing.
        """
        cache = caches.get(self.cache_name)

        for key in self.keys:
            to_remove_values = self.previous[key] - self.current[key]
            for to_remove in to_remove_values:
                yield key, to_remove
            cache.set(key, self.current[key])

    @staticmethod
    def close() -> None:
        """
        Unregister and close the underlying cache.
        """
        caches.unregister("traefik.extra-services", callback=lambda c: c.close())
