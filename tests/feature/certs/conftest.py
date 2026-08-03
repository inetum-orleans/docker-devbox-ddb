import hashlib
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID


def _pem(builder_output: Any) -> str:
    return builder_output.public_bytes(serialization.Encoding.PEM).decode("ascii")


def _sums(pem: str, part: str) -> dict[str, str]:
    loader = x509.load_pem_x509_certificate if part == "certificate" else x509.load_pem_x509_csr
    der = loader(pem.encode("ascii")).public_bytes(serialization.Encoding.DER)
    return {"sha-256": hashlib.sha256(der).hexdigest()}


@pytest.fixture(scope="module")
def response() -> dict[str, Any]:
    """
    A cfssl-shaped response, built from a self-signed certificate and its certificate request.
    """
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "testing.test")])

    certificate = _pem(
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(UTC) - timedelta(days=1))
        .not_valid_after(datetime.now(UTC) + timedelta(days=1))
        .sign(private_key, hashes.SHA256())
    )
    certificate_request = _pem(
        x509.CertificateSigningRequestBuilder().subject_name(subject).sign(private_key, hashes.SHA256())
    )

    return {
        "private_key": private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode("ascii"),
        "certificate": certificate,
        "certificate_request": certificate_request,
        "sums": {
            "certificate": _sums(certificate, "certificate"),
            "certificate_request": _sums(certificate_request, "certificate_request"),
        },
    }
