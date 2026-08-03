import dbm
import shelve
import tempfile
from pathlib import Path

from ..config import config
from .cache import Cache

# Easy fix for https://github.com/inetum-orleans/docker-devbox-ddb/issues/49
_dbm_names = dbm._names = ["dbm.gnu", "dbm.ndbm", "dbm.dumb"]  # type: ignore[attr-defined]
if "dbm.dumb" in _dbm_names:
    # Let's make dbm.dumb the preferred implementation
    _dbm_names.remove("dbm.dumb")
    _dbm_names.insert(0, "dbm.dumb")
    dbm._names = _dbm_names  # type: ignore[attr-defined]


class ShelveCache(Cache):
    """
    A cache implementation relying of shelve module.
    """

    def __init__(self, namespace: str, *, eternal=False):
        super().__init__(namespace)

        clear_cache = config.clear_cache and not eternal

        path = Path(config.paths.home) / "cache" if config.paths.home else Path(tempfile.gettempdir()) / "ddb" / "cache"
        path.mkdir(parents=True, exist_ok=True)

        self.basename = str(path / self._namespace)
        if clear_cache:
            self._delete_files(self.basename)
        try:
            self._shelf = shelve.open(self.basename)
        except Exception as open_error:
            if self._delete_files(self.basename):
                try:
                    self._shelf = shelve.open(self.basename)
                except Exception as fallback_error:
                    raise open_error from fallback_error
            else:
                raise
        if clear_cache:
            self._shelf.clear()

    @staticmethod
    def _delete_files(basename):
        deleted = False
        for filename in (basename, f"{basename}.dat", f"{basename}.dir"):
            if Path(filename).exists():
                Path(filename).unlink()
                deleted = True
        return deleted

    def close(self):
        self._shelf.close()

    def flush(self):
        self._shelf.sync()

    def get(self, key: str, default=None):
        try:
            return self._shelf.get(key, default)
        except AttributeError:
            # This can occur when class definition hash change.
            self._delete_files(self.basename)
            raise

    def keys(self):
        return self._shelf.keys()

    def set(self, key: str, data):
        self._shelf[key] = data

    def pop(self, key: str):
        try:
            return self._shelf.pop(key)
        except AttributeError:
            # This can occur when class definition hash change.
            self._delete_files(self.basename)
            raise

    def clear(self):
        try:
            self._shelf.clear()
        except AttributeError:
            # This can occur when class definition hash change.
            self._delete_files(self.basename)
            raise

    def __contains__(self, key):
        return self._shelf.__contains__(key)
