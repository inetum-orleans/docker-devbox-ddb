from collections import defaultdict

from ddb.cache import register_project_cache, caches


class RemovalCacheSupport:  # pylint:disable=too-many-instance-attributes
    """
    Handle a cache to support removal of previously generated resources when they are not linked to the current
    configuration anymore.
    """

    def __init__(self, cache_name, keys):
        self.cache_name = cache_name
        self.keys = set(keys)
        self.type = set

        self.cached = defaultdict(self.type)
        self.previous = defaultdict(self.type)
        self.current = defaultdict(self.type)

        register_project_cache(self.cache_name)

    def prepare(self):
        """
        This should be called before processing extra-services configuration.
        """
        cache = caches.get(self.cache_name)

        for key in self.keys:
            self.cached[key] = cache.get(key, self.type())
            self.previous[key] = self.type(self.cached[key])
            self.current[key] = self.type()

    def set_current_value(self, key, value):
        """
        Set current value for given key.
        """
        if key not in self.keys:
            raise ValueError("Given key '%s' doesn't match any of the supported key %s" % (key, self.keys))
        self.cached[key].add(value)
        self.current[key].add(value)

    def get_removed(self):
        """
        This should be called after processing. Generates (key, value) to remove.
        """
        cache = caches.get(self.cache_name)

        for key in self.keys:
            to_remove_values = self.previous[key] - self.current[key]
            for to_remove in to_remove_values:
                yield key, to_remove
            cache.set(key, self.current[key])

    @staticmethod
    def close():
        """
        Unregister and close the underlying cache.
        """
        caches.unregister("traefik.extra-services", callback=lambda c: c.close())
