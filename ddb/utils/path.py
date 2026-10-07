import os
from pathlib import Path


def absolute_path(path: str | os.PathLike[str]) -> str:
    """
    Make a path absolute and lexically normalized, leaving symbolic links unexpanded.
    """
    # os.path.normpath has no pathlib counterpart, and Path.resolve() would also expand
    # symlinks: generated paths are compared as strings against the configured project
    # home, which is not expanded either.
    return os.path.normpath(Path(path).absolute())
