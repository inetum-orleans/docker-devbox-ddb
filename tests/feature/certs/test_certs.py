from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID

from ddb.__main__ import load_registered_features
from ddb.config import config
from ddb.feature import features
from ddb.feature.certs import CertsFeature, GenerateCertAction
from ddb.feature.certs.actions import (
    GenerateSignerCertificateAction,
    RemoveCertAction,
    certificate_should_be_generated,
)
from ddb.feature.certs.cfssl.crypto import get_certificate_expiration
from ddb.feature.core import CoreFeature
from tests.utilstest import setup_cfssl


def write_self_signed_certificate(path: Path, *, expires_in_days: float) -> None:
    """
    Write a self signed certificate expiring in the given number of days, which may be negative.
    """
    key = ec.generate_private_key(ec.SECP256R1())
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "testing.test")])
    now = datetime.now(UTC)

    certificate = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(days=365))
        .not_valid_after(now + timedelta(days=expires_in_days))
        .sign(key, hashes.SHA256())
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(certificate.public_bytes(serialization.Encoding.PEM))


class TestCertsFeature:
    @pytest.mark.docker
    def test_empty_project_without_core(self, project_loader, module_scoped_container_getter):
        project_loader("empty")

        features.register(CertsFeature())
        load_registered_features()

        setup_cfssl(module_scoped_container_getter)

        generate_action = GenerateCertAction()
        generate_action.execute(domain="testing.test")

        assert (Path(".certs") / "testing.test.crt").exists()
        assert (Path(".certs") / "testing.test.key").exists()

        remove_action = RemoveCertAction()
        remove_action.execute(domain="testing.test")
        assert not (Path(".certs") / "testing.test.crt").exists()
        assert not (Path(".certs") / "testing.test.key").exists()

    @pytest.mark.docker
    def test_empty_project_with_core(self, project_loader, module_scoped_container_getter):
        project_loader("empty")

        features.register(CoreFeature())
        features.register(CertsFeature())
        load_registered_features()

        setup_cfssl(module_scoped_container_getter)

        generate_action = GenerateCertAction()
        generate_action.execute(domain="testing.test")

        assert (Path(".certs") / "testing.test.crt").exists()
        assert (Path(".certs") / "testing.test.key").exists()

        with (Path(".certs") / "testing.test.crt").open() as crt_file:
            assert "CERTIFICATE" in crt_file.read()

        with (Path(".certs") / "testing.test.key").open() as key_file:
            assert "PRIVATE KEY" in key_file.read()

        remove_action = RemoveCertAction()
        remove_action.execute(domain="testing.test")
        assert not (Path(".certs") / "testing.test.crt").exists()
        assert not (Path(".certs") / "testing.test.key").exists()

    @pytest.mark.docker
    def test_in_date_does_nothing(self, project_loader, module_scoped_container_getter):
        project_loader("empty")

        features.register(CoreFeature())
        features.register(CertsFeature())
        load_registered_features()

        setup_cfssl(module_scoped_container_getter)

        generate_action = GenerateCertAction()
        generate_action.execute(domain="testing.test")

        with (Path(".certs") / "testing.test.crt").open() as crt_file:
            crt = crt_file.read()

        with (Path(".certs") / "testing.test.key").open() as key_file:
            key = key_file.read()

        generate_action.execute(domain="testing.test")

        with (Path(".certs") / "testing.test.crt").open() as crt_file:
            assert crt == crt_file.read()

        with (Path(".certs") / "testing.test.key").open() as key_file:
            assert key == key_file.read()

        remove_action = RemoveCertAction()
        remove_action.execute(domain="testing.test")

        assert not (Path(".certs") / "testing.test.crt").exists()
        assert not (Path(".certs") / "testing.test.key").exists()

    @pytest.mark.docker
    def test_expired_is_generated_again(self, project_loader, module_scoped_container_getter):
        project_loader("existing")

        features.register(CoreFeature())
        features.register(CertsFeature())
        load_registered_features()

        setup_cfssl(module_scoped_container_getter)

        # The committed fixture certificate expired on 2021-04-12.
        expired_crt = (Path(".certs") / "testing.test.crt").read_bytes()
        assert get_certificate_expiration(expired_crt) < datetime.now(UTC)

        generate_action = GenerateCertAction()
        generate_action.execute(domain="testing.test")

        renewed_crt = (Path(".certs") / "testing.test.crt").read_bytes()
        assert renewed_crt != expired_crt
        assert get_certificate_expiration(renewed_crt) > datetime.now(UTC)

    @pytest.mark.docker
    def test_expiring_within_margin_is_generated_again(self, project_loader, module_scoped_container_getter):
        project_loader("empty")

        features.register(CoreFeature())
        features.register(CertsFeature())
        load_registered_features()

        setup_cfssl(module_scoped_container_getter)

        certificate = Path(".certs") / "testing.test.crt"
        write_self_signed_certificate(certificate, expires_in_days=5)
        # The private key is only looked for, never read, so its content does not matter here.
        (Path(".certs") / "testing.test.key").write_text("private key")
        expiring_crt = certificate.read_bytes()

        config.data["certs.renew_before_days"] = 30

        generate_action = GenerateCertAction()
        generate_action.execute(domain="testing.test")

        renewed_crt = certificate.read_bytes()
        assert renewed_crt != expiring_crt
        assert get_certificate_expiration(renewed_crt) > datetime.now(UTC) + timedelta(days=30)

    @pytest.mark.docker
    def test_missing_private_key_is_generated_again(self, project_loader, module_scoped_container_getter):
        project_loader("empty")

        features.register(CoreFeature())
        features.register(CertsFeature())
        load_registered_features()

        setup_cfssl(module_scoped_container_getter)

        generate_action = GenerateCertAction()
        generate_action.execute(domain="testing.test")

        private_key = Path(".certs") / "testing.test.key"
        crt = (Path(".certs") / "testing.test.crt").read_bytes()
        private_key.unlink()

        generate_action.execute(domain="testing.test")

        assert private_key.exists()
        assert (Path(".certs") / "testing.test.crt").read_bytes() != crt


@pytest.mark.docker
class TestSignerCertificate:
    """
    Check the signer certificate is refreshed on the same rule as domain certificates.
    """

    @pytest.fixture(autouse=True)
    def _load_certs_feature(self, project_loader, module_scoped_container_getter):
        project_loader("empty")

        features.register(CoreFeature())
        features.register(CertsFeature())
        load_registered_features()

        setup_cfssl(module_scoped_container_getter)

    def test_in_date_signer_does_nothing(self):
        signer = Path(".certs") / ".signer.crt"

        GenerateSignerCertificateAction().execute()
        assert signer.exists()
        generated = signer.read_bytes()

        GenerateSignerCertificateAction().execute()
        assert signer.read_bytes() == generated

    def test_expired_signer_is_generated_again(self):
        signer = Path(".certs") / ".signer.crt"

        GenerateSignerCertificateAction().execute()
        write_self_signed_certificate(signer, expires_in_days=-1)
        expired = signer.read_bytes()

        GenerateSignerCertificateAction().execute()

        renewed = signer.read_bytes()
        assert renewed != expired
        assert get_certificate_expiration(renewed) > datetime.now(UTC)

    def test_renewed_signer_reaches_signer_destinations(self):
        signer = Path(".certs") / ".signer.crt"
        installed = Path("ca") / "root.crt"
        config.data["certs.signer_destinations"] = [str(installed)]

        GenerateSignerCertificateAction().execute()
        assert installed.read_bytes() == signer.read_bytes()

        write_self_signed_certificate(signer, expires_in_days=-1)
        expired = signer.read_bytes()

        GenerateSignerCertificateAction().execute()

        assert installed.read_bytes() == signer.read_bytes()
        assert installed.read_bytes() != expired


class TestCertificateShouldBeGenerated:
    """
    Check when an existing certificate is considered good enough to be kept.
    """

    @pytest.fixture(autouse=True)
    def _load_certs_feature(self, project_loader):
        project_loader("empty")

        features.register(CoreFeature())
        features.register(CertsFeature())
        load_registered_features()

    def test_missing_certificate(self):
        assert certificate_should_be_generated("absent.crt")

    def test_in_date_certificate(self, tmp_path):
        certificate = tmp_path / "testing.test.crt"
        write_self_signed_certificate(certificate, expires_in_days=365)

        assert not certificate_should_be_generated(str(certificate))

    def test_expired_certificate(self, tmp_path):
        certificate = tmp_path / "testing.test.crt"
        write_self_signed_certificate(certificate, expires_in_days=-1)

        assert certificate_should_be_generated(str(certificate))

    def test_certificate_expiring_within_margin(self, tmp_path):
        certificate = tmp_path / "testing.test.crt"
        write_self_signed_certificate(certificate, expires_in_days=29)
        config.data["certs.renew_before_days"] = 30

        assert certificate_should_be_generated(str(certificate))

    def test_certificate_expiring_after_margin(self, tmp_path):
        certificate = tmp_path / "testing.test.crt"
        write_self_signed_certificate(certificate, expires_in_days=31)
        config.data["certs.renew_before_days"] = 30

        assert not certificate_should_be_generated(str(certificate))

    def test_zero_margin_keeps_certificate_until_expiration(self, tmp_path):
        certificate = tmp_path / "testing.test.crt"
        write_self_signed_certificate(certificate, expires_in_days=1)
        config.data["certs.renew_before_days"] = 0

        assert not certificate_should_be_generated(str(certificate))

    def test_unreadable_certificate(self, tmp_path):
        certificate = tmp_path / "testing.test.crt"
        certificate.write_text("not a certificate")

        assert certificate_should_be_generated(str(certificate))
