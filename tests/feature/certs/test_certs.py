from pathlib import Path

import pytest

from ddb.__main__ import load_registered_features
from ddb.feature import features
from ddb.feature.certs import CertsFeature, GenerateCertAction
from ddb.feature.certs.actions import RemoveCertAction
from ddb.feature.core import CoreFeature
from tests.utilstest import setup_cfssl


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
    def test_existing_does_nothing(self, project_loader, module_scoped_container_getter):
        project_loader("existing")

        features.register(CoreFeature())
        features.register(CertsFeature())
        load_registered_features()

        setup_cfssl(module_scoped_container_getter)

        assert (Path(".certs") / "testing.test.crt").exists()
        assert (Path(".certs") / "testing.test.key").exists()

        with (Path(".certs") / "testing.test.crt").open() as crt_file:
            crt = crt_file.read()

        with (Path(".certs") / "testing.test.key").open() as key_file:
            key = key_file.read()

        generate_action = GenerateCertAction()
        generate_action.execute(domain="testing.test")

        with (Path(".certs") / "testing.test.crt").open() as crt_file:
            assert crt == crt_file.read()

        with (Path(".certs") / "testing.test.key").open() as key_file:
            assert key == key_file.read()

        remove_action = RemoveCertAction()
        remove_action.execute(domain="testing.test")

        assert not (Path(".certs") / "testing.test.crt").exists()
        assert not (Path(".certs") / "testing.test.key").exists()
