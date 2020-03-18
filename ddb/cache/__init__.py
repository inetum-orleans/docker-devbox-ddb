# -*- coding: utf-8 -*-
from .cache import Cache
from .shelve_cache import ShelveCache
from ..registry import Registry

caches = Registry(Cache, 'Cache')  # type: Registry[Cache]

_global_cache_name = 'global'
_project_cache_name = 'project'
_requests_cache_name = 'requests'


def global_cache() -> Cache:
    """
    Get global cache.
    """
    return caches.get(_global_cache_name)


def project_cache() -> Cache:
    """
    Get current project cache.
    """
    return caches.get(_project_cache_name)
