# -*- coding: utf-8 -*-
"""
Crypto module
"""

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization


class CryptoException(Exception):
    """
    Exception raised when something wrong occurs in cryto module.
    """


def convert_pem_to_der(part, content):
    """
    Converts a PEM certificate, csr or crl to DER
    :param part: type of object to convert
    :type part: byte[]
    :param content: PEM data as a ASCII string
    :type content: str
    :return: DER Encoded object
    :rtype: byte[]
    """
    if part == 'certificate':
        cert = x509.load_pem_x509_certificate(content, default_backend())
        return cert.public_bytes(serialization.Encoding.DER)
    if part == 'certificate_request':
        csr = x509.load_pem_x509_csr(content, default_backend())
        return csr.public_bytes(serialization.Encoding.DER)
    raise CryptoException('Unknown object type: %s' % part)
