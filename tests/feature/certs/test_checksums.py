import pytest

from ddb.feature.certs.cfssl.checksums import validate_checksums
from ddb.feature.certs.cfssl.crypto import CryptoException, convert_pem_to_der


class TestValidateChecksums:
    def test_matching_checksums_are_accepted(self, response):
        validate_checksums(response)

    def test_parts_without_checksum_are_skipped(self, response):
        validate_checksums({**response, "sums": {}})

    def test_invalid_checksum_is_rejected(self, response):
        tampered = {**response, "sums": {**response["sums"], "certificate": {"sha-256": "0" * 64}}}

        with pytest.raises(OSError, match="Invalid certificate checksum"):
            validate_checksums(tampered)


class TestConvertPemToDer:
    def test_unknown_part_is_rejected(self):
        with pytest.raises(CryptoException, match="Unknown object type: certificate_revocation_list"):
            convert_pem_to_der("certificate_revocation_list", b"")
