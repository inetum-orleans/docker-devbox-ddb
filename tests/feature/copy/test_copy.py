from pathlib import Path

from ddb.__main__ import load_registered_features, register_default_caches
from ddb.feature import features
from ddb.feature.copy import CopyAction, CopyFeature


class TestCopyFeature:
    def test_copy_ca_certificates(self, project_loader):
        project_loader("copy-ca-certificates")

        features.register(CopyFeature())
        load_registered_features()

        action = CopyAction()
        action.execute()

        assert (Path(".docker") / "service1" / "ca-certs" / "some-cert.crt").exists()
        assert not (Path(".docker") / "service1" / "ca-certs" / "another-cert.crt").exists()

        assert (Path(".docker") / "service2" / "ca-certs" / "some-cert.crt").exists()
        assert not (Path(".docker") / "service2" / "ca-certs" / "another-cert.crt").exists()

        assert not (Path(".docker") / ".not-a-service" / "ca-certs" / "some-cert.crt").exists()
        assert not (Path(".docker") / ".not-a-service" / "ca-certs" / "another-cert.crt").exists()

    def test_copy_fixuid(self, project_loader):
        project_loader("copy-fixuid")

        features.register(CopyFeature())
        load_registered_features()
        register_default_caches()

        action = CopyAction()
        action.execute()

        assert (Path(".docker") / "service1" / "fixuid.tar.gz").exists()
        assert (Path(".docker") / "service2" / "fixuid.tar.gz").exists()
        assert not (Path(".docker") / ".not-a-service" / "fixuid.tar.gz").exists()

    def test_copy_fixuid_default_filename(self, project_loader):
        project_loader("copy-fixuid-default-filename")

        features.register(CopyFeature())
        load_registered_features()
        register_default_caches()

        action = CopyAction()
        action.execute()

        assert (Path(".docker") / "service1" / "fixuid-0.5-linux-amd64.tar.gz").exists()
        assert (Path(".docker") / "service2" / "fixuid-0.5-linux-amd64.tar.gz").exists()
        assert not (Path(".docker") / ".not-a-service" / "fixuid-0.5-linux-amd64.tar.gz").exists()

    def test_copy_no_dispatch(self, project_loader):
        project_loader("copy-no-dispatch")

        features.register(CopyFeature())
        load_registered_features()
        register_default_caches()

        action = CopyAction()
        action.execute()
        assert Path("some-cert.crt").exists()

    def test_copy_subdirectory(self, project_loader):
        project_loader("copy-subdirectory")

        features.register(CopyFeature())
        load_registered_features()
        register_default_caches()

        action = CopyAction()
        action.execute()
        assert (Path("sub") / "target").exists()

        assert (Path("sub") / "target" / "test.abc.json").is_file()
        assert (Path("sub") / "target" / "test.def.json").is_file()
        assert (Path("sub") / "target" / "test.ijk.yaml").is_file()

    def test_copy_subdirectory_glob(self, project_loader):
        project_loader("copy-subdirectory-glob")

        features.register(CopyFeature())
        load_registered_features()
        register_default_caches()

        action = CopyAction()
        action.execute()
        assert (Path("sub") / "target").exists()

        assert (Path("sub") / "target" / "test.abc.json").is_file()
        assert (Path("sub") / "target" / "test.def.json").is_file()
        assert not (Path("sub") / "target" / "test.ijk.yaml").exists()
