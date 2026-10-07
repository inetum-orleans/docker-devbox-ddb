"""
Checksums module.
"""

import hashlib
from typing import Any

from .crypto import convert_pem_to_der


def validate_checksums(response: dict[str, Any]) -> None:
    """
    Validate checksums from certificate request response.

    :param response:
    :return:
    """
    sums = response.get("sums", {})
    for part, content in response.items():
        if part not in ("sums", "private_key"):
            sums_item = sums.get(part)
            if not sums_item:
                continue
            validate_checksum(part, content.encode("ascii"), sums_item)


def validate_checksum(part: str, content: bytes, sums_item: dict[str, str], *, content_is_der: bool = False) -> None:
    """
    Validate a checksum from certificate sums and content.

    :param part:
    :param content:
    :param sums_item:
    :param content_is_der:
    :return:
    """
    for algo, checksum in sums_item.items():
        validate_checksum_algo(part, content, algo, checksum, content_is_der=content_is_der)


def validate_checksum_algo(
    part: str, content: bytes, algo: str, checksum: str, *, content_is_der: bool = False
) -> None:
    """
    Validate a checksum using content, algo and checksum.

    :param part:
    :param content:
    :param algo:
    :param checksum:
    :param content_is_der:
    :return:
    """
    if not content_is_der:
        content = convert_pem_to_der(part, content)

    validated_checksum = getattr(hashlib, algo.replace("-", ""))(content).hexdigest()
    checksum = checksum.lower()
    if validated_checksum != checksum:
        msg = f"Invalid {part} checksum ({algo}): {checksum} != {validated_checksum} "
        raise OSError(msg)
