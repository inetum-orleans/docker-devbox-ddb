# -*- coding: utf-8 -*-
from uuid import uuid4

from slugify import slugify

from .cache import Cache
from .shelve_cache import ShelveCache
from ..config import config
from ..registry import Registry

caches = Registry(Cache, 'Cache')  # type: Registry[Cache]

global_cache_name = 'global'
requests_cache_name = 'requests'

project_cache_name = 'project'
project_binary_cache_name = 'binary'


def register_project_cache(cache_name):
    """
    Creates a ShelveCache for current project, and register it with given name.
    """
    registered_projects_cache_name = ShelveCache('project-cache-uuid', eternal=True)
    try:
        project_cache_uuid = registered_projects_cache_name.get(config.paths.project_home)
        if project_cache_uuid is None:
            project_cache_uuid = str(uuid4())
            registered_projects_cache_name.set(config.paths.project_home, project_cache_uuid)
    finally:
        registered_projects_cache_name.close()

    namespace = [item for item in (project_cache_uuid, cache_name) if item]
    cache = ShelveCache(slugify('.'.join(namespace), regex_pattern=r'[^-a-z0-9_\.]+'))

    caches.register(cache, cache_name)
    return cache


def register_global_cache(cache_name):
    """
    Creates a ShelveCache shared for all projects, and register it with given name.
    """
    cache = ShelveCache(slugify(cache_name, regex_pattern=r'[^-a-z0-9_\.]+'))
    caches.register(cache, cache_name)
    return cache


def global_cache() -> Cache:
    """
    Get global cache.
    """
    return caches.get(global_cache_name)


def project_cache() -> Cache:
    """
    Get current project cache.
    """
    return caches.get(project_cache_name)


def requests_cache() -> Cache:
    """
    Get current requests cache.
    """
    return caches.get(requests_cache_name)
