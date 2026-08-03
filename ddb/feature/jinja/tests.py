import glob


def found_with_glob(value: str) -> bool:
    """
    Check if at least one file match the given glob expression.

    :param value: glob expression.
    """
    # PTH207: expressions come from user templates and may be absolute, which Path.glob
    # rejects, and Path.glob would also match hidden entries that glob.glob leaves out.
    for _ in glob.glob(value):  # noqa: PTH207
        return True
    return False
