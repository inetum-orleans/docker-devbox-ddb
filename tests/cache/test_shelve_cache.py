from pathlib import Path

import pytest
from _pytest.fixtures import FixtureRequest
from pytest_mock import MockerFixture

from ddb.cache.shelve_cache import ShelveCache
from ddb.config import config


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

    def test_should_expose_membership(self, request: FixtureRequest):
        adapter = ShelveCache(request.node.name)
        adapter.set("foo", "bar")

        assert "foo" in adapter
        assert "bar" not in adapter

    def test_should_start_empty_when_cache_is_cleared(self, request: FixtureRequest):
        adapter = ShelveCache(request.node.name)
        adapter.set("foo", "bar")
        adapter.close()

        config.args.clear_cache = True

        assert ShelveCache(request.node.name).get("foo") is None

    def test_should_keep_eternal_cache_when_cache_is_cleared(self, request: FixtureRequest):
        adapter = ShelveCache(request.node.name, eternal=True)
        adapter.set("foo", "bar")
        adapter.close()

        config.args.clear_cache = True

        assert ShelveCache(request.node.name, eternal=True).get("foo") == "bar"

    def test_should_delete_unreadable_files_and_open_again(self, request: FixtureRequest, mocker: MockerFixture):
        ShelveCache(request.node.name).close()

        shelve_open = mocker.patch("shelve.open", side_effect=[ValueError("unreadable"), mocker.MagicMock()])

        ShelveCache(request.node.name)

        assert shelve_open.call_count == 2

    def test_should_raise_the_original_error_when_opening_again_fails(
        self, request: FixtureRequest, mocker: MockerFixture
    ):
        ShelveCache(request.node.name).close()

        mocker.patch("shelve.open", side_effect=[ValueError("unreadable"), ValueError("still unreadable")])

        with pytest.raises(ValueError, match=r"^unreadable$"):
            ShelveCache(request.node.name)

    def test_should_raise_when_there_is_no_file_to_delete(self, request: FixtureRequest, mocker: MockerFixture):
        mocker.patch("shelve.open", side_effect=ValueError("unreadable"))

        with pytest.raises(ValueError, match=r"^unreadable$"):
            ShelveCache(request.node.name)


class TestShelveAdapterStaleShelf:
    """
    A shelf holding pickled instances of a class whose definition changed raises AttributeError. The cache files are
    then deleted so the next run starts from a readable state.
    """

    @staticmethod
    def _stale_adapter(request: FixtureRequest, mocker: MockerFixture) -> ShelveCache:
        adapter = ShelveCache(request.node.name)
        adapter.set("foo", "bar")
        adapter.flush()

        stale = {
            "get.side_effect": AttributeError,
            "pop.side_effect": AttributeError,
            "clear.side_effect": AttributeError,
        }
        mocker.patch.object(adapter, "_shelf", **stale)

        return adapter

    @staticmethod
    def _assert_files_deleted(adapter: ShelveCache) -> None:
        basename = adapter.basename
        assert not any(Path(filename).exists() for filename in (basename, f"{basename}.dat", f"{basename}.dir"))

    def test_get_should_delete_files_and_raise(self, request: FixtureRequest, mocker: MockerFixture):
        adapter = self._stale_adapter(request, mocker)

        with pytest.raises(AttributeError):
            adapter.get("foo")

        self._assert_files_deleted(adapter)

    def test_pop_should_delete_files_and_raise(self, request: FixtureRequest, mocker: MockerFixture):
        adapter = self._stale_adapter(request, mocker)

        with pytest.raises(AttributeError):
            adapter.pop("foo")

        self._assert_files_deleted(adapter)

    def test_clear_should_delete_files_and_raise(self, request: FixtureRequest, mocker: MockerFixture):
        adapter = self._stale_adapter(request, mocker)

        with pytest.raises(AttributeError):
            adapter.clear()

        self._assert_files_deleted(adapter)
