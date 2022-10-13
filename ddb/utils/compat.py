import re

_windows_drive_letter_regex = re.compile(r"^([a-zA-Z]):")
_windows_posix_drive_letter_regex = re.compile(r"^/([a-z])(/|$)")


def path_as_posix_fast(path: str):
    """
    Convert a local path to a posix path
    """
    replaced = _windows_drive_letter_regex.sub(lambda match: '/' + match.group(1).lower(), path)
    return replaced.replace('\\', '/')


def posix_as_path_fast(posix_path: str):
    """
    Convert a posix path to a local path
    """
    replaced = _windows_posix_drive_letter_regex.sub(lambda match: match.group(1).upper() + ':' + match.group(2),
                                                     posix_path)
    return replaced.replace('/', '\\')
