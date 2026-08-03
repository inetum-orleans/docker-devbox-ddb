from pathlib import Path

import pytest
from _pytest.capture import CaptureFixture

from ddb.feature.certs.cfssl.crypto import convert_pem_to_der
from ddb.feature.certs.cfssl.writer import get_certs_path, write_files, write_stdout


class TestGetCertsPath:
    def test_default_filenames(self):
        assert get_certs_path("testing.test") == ("testing.test.pem", "testing.test.key.pem")

    def test_configured_filenames(self):
        conf = {"filenames": {"certificate": "%s.crt", "private_key": "%s.key"}}

        assert get_certs_path("testing.test", conf) == ("testing.test.crt", "testing.test.key")

    def test_destination_from_configuration(self, tmp_path):
        conf = {"destination": str(tmp_path)}

        certificate, private_key = get_certs_path("testing.test", conf)

        assert certificate == str(tmp_path / "testing.test.pem")
        assert private_key == str(tmp_path / "testing.test.key.pem")

    def test_destination_argument_wins_over_configuration(self, tmp_path):
        conf = {"destination": str(tmp_path / "from-conf")}

        certificate, _ = get_certs_path("testing.test", conf, str(tmp_path / "from-argument"))

        assert certificate == str(tmp_path / "from-argument" / "testing.test.pem")


class TestWriteFiles:
    def test_certificate_and_private_key_are_written(self, response, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        generated = write_files(response, "testing.test")

        assert set(generated) == {"private_key", "certificate"}
        assert Path(generated["certificate"]).read_text() == response["certificate"]
        assert Path(generated["private_key"]).read_text() == response["private_key"]

    def test_certificate_request_is_written_on_demand(self, response, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        generated = write_files(response, "testing.test", csr=True)

        assert Path(generated["certificate_request"]).read_text() == response["certificate_request"]

    def test_der_files_are_written_on_demand(self, response, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        generated = write_files(response, "testing.test", csr=True, der=True)

        assert set(generated) == {
            "private_key",
            "certificate",
            "certificate_request",
            "certificate_der",
            "certificate_request_der",
        }
        assert Path(generated["certificate_der"]).read_bytes().startswith(b"\x30\x82")

    def test_der_files_are_written_in_the_destination_directory(self, response, tmp_path):
        destination = tmp_path / "certs"
        destination.mkdir()

        generated = write_files(response, "testing.test", destination=str(destination), csr=True, der=True)

        for path in generated.values():
            assert Path(path).parent == destination

    def test_configured_filenames_are_honored(self, response, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        conf = {"filenames": {"certificate": "%s.crt", "private_key": "%s.key", "certificate_request": "%s.csr"}}

        generated = write_files(response, "testing.test", conf, csr=True)

        assert Path(generated["certificate"]).name == "testing.test.crt"
        assert Path(generated["private_key"]).name == "testing.test.key"
        assert Path(generated["certificate_request"]).name == "testing.test.csr"

    def test_destination_from_configuration_is_honored(self, response, tmp_path):
        destination = tmp_path / "certs"
        destination.mkdir()

        generated = write_files(response, "testing.test", {"destination": str(destination)})

        assert Path(generated["certificate"]).parent == destination

    def test_invalid_checksum_is_rejected(self, response, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        tampered = {**response, "sums": {**response["sums"], "certificate": {"sha-256": "0" * 64}}}

        with pytest.raises(OSError, match="Invalid certificate checksum"):
            write_files(tampered, "testing.test")

    def test_ca_certificate_is_appended(self, response, tmp_path, monkeypatch, mocker):
        monkeypatch.chdir(tmp_path)
        client = mocker.Mock()
        client.info.return_value = {"certificate": response["certificate"].strip()}

        generated = write_files(response, "testing.test", append_ca_certificate=True, client=client, der=True)

        assert Path(generated["certificate"]).read_text().count("BEGIN CERTIFICATE") == 2


class TestWriteStdout:
    def test_pem_content_is_printed(self, response, capsys: CaptureFixture):
        write_stdout(response)

        out = capsys.readouterr().out
        assert response["private_key"] in out
        assert response["certificate"] in out
        assert response["certificate_request"] in out

    def test_der_content_is_printed_on_demand(self, response, capsys: CaptureFixture):
        write_stdout(response, der=True, csr=True)

        out = capsys.readouterr().out
        assert str(convert_pem_to_der("certificate", response["certificate"].encode("ascii"))) in out
        assert str(convert_pem_to_der("certificate_request", response["certificate_request"].encode("ascii"))) in out

    def test_ca_certificate_is_printed(self, response, capsys: CaptureFixture, mocker):
        client = mocker.Mock()
        client.info.return_value = {"certificate": response["certificate"].strip()}

        write_stdout(response, append_ca_certificate=True, client=client)

        assert capsys.readouterr().out.count("BEGIN CERTIFICATE") == 3
