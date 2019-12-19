from ddb.__main__ import register_default_caches
from ddb.cache import global_cache, project_cache


def test_global_cache():
    register_default_caches()
    assert global_cache() is not None


def test_project_cache():
    register_default_caches()
    assert project_cache() is not None
