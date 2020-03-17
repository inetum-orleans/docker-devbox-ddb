import glob


def found_with_glob(value):
    """
    Check if at least one file match the given glob expression.
    :param value: glob expression
    """
    for _ in glob.glob(value):
        return True
    return False
