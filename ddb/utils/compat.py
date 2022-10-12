import re

_posix_drive_letter_regex = re.compile(r"^([a-zA-Z]):")


def path_as_posix_fast(path: str):
    """
    Simpler but faster version of pathlib Path.as_posix method
    """
    path = _posix_drive_letter_regex.sub(lambda match: '/' + match.group(1).lower(), path)
    return path.replace('\\', '/')
