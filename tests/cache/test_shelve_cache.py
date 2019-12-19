import pytest
from _pytest.fixtures import FixtureRequest

from ddb.cache.shelve_cache import ShelveCache


class TestShelveAdapter:
    def test_should_raise_value_error_set_after_close(self, request: FixtureRequest):
        adapter = ShelveCache(request.node.name)
        adapter.close()

        with pytest.raises(ValueError):
            adapter.set("foo", "bar")

    def test_should_set_value_properly(self, request: FixtureRequest):
        adapter = ShelveCache(request.node.name)
        adapter.set("foo", "bar")

        adapter.flush()
        assert adapter.get("foo") == "bar"

        adapter.close()

        adapter = ShelveCache(request.node.name)
        assert adapter.get("foo") == "bar"

    def test_should_set_number_value_properly(self, request: FixtureRequest):
        adapter = ShelveCache(request.node.name)
        adapter.set("foo", 1337)

        adapter.flush()
        assert adapter.get("foo") == 1337

        adapter.close()

        adapter = ShelveCache(request.node.name)
        assert adapter.get("foo") == 1337

    def test_should_clear_value_properly(self, request: FixtureRequest):
        adapter = ShelveCache(request.node.name)
        adapter.set("foo", "bar")

        adapter.close()
        adapter = ShelveCache(request.node.name)
        adapter.set("foo", "bar")

        adapter.clear()
        adapter.close()

        adapter = ShelveCache(request.node.name)
        assert adapter.get("foo") is None
