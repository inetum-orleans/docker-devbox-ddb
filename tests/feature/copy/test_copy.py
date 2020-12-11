import os

from ddb.__main__ import load_registered_features, register_default_caches
from ddb.feature import features
from ddb.feature.copy import CopyFeature, CopyAction


class TestCopyFeature:
    def test_copy_ca_certificates(self, project_loader):
        project_loader("copy-ca-certificates")

        features.register(CopyFeature())
        load_registered_features()

        action = CopyAction()
        action.execute()

        assert os.path.exists(os.path.join('.docker', 'service1', 'ca-certs', 'some-cert.crt'))
        assert not os.path.exists(os.path.join('.docker', 'service1', 'ca-certs', 'another-cert.crt'))

        assert os.path.exists(os.path.join('.docker', 'service2', 'ca-certs', 'some-cert.crt'))
        assert not os.path.exists(os.path.join('.docker', 'service2', 'ca-certs', 'another-cert.crt'))

        assert not os.path.exists(os.path.join('.docker', '.not-a-service', 'ca-certs', 'some-cert.crt'))
        assert not os.path.exists(os.path.join('.docker', '.not-a-service', 'ca-certs', 'another-cert.crt'))

    def test_copy_fixuid(self, project_loader):
        project_loader("copy-fixuid")

        features.register(CopyFeature())
        load_registered_features()
        register_default_caches()

        action = CopyAction()
        action.execute()

        assert os.path.exists(os.path.join('.docker', 'service1', 'fixuid.tar.gz'))
        assert os.path.exists(os.path.join('.docker', 'service2', 'fixuid.tar.gz'))
        assert not os.path.exists(os.path.join('.docker', '.not-a-service', 'fixuid.tar.gz'))

    def test_copy_fixuid_default_filename(self, project_loader):
        project_loader("copy-fixuid-default-filename")

        features.register(CopyFeature())
        load_registered_features()
        register_default_caches()

        action = CopyAction()
        action.execute()

        assert os.path.exists(os.path.join('.docker', 'service1', 'fixuid-0.5-linux-amd64.tar.gz'))
        assert os.path.exists(os.path.join('.docker', 'service2', 'fixuid-0.5-linux-amd64.tar.gz'))
        assert not os.path.exists(os.path.join('.docker', '.not-a-service', 'fixuid-0.5-linux-amd64.tar.gz'))

    def test_copy_no_dispatch(self, project_loader):
        project_loader("copy-no-dispatch")

        features.register(CopyFeature())
        load_registered_features()
        register_default_caches()

        action = CopyAction()
        action.execute()
        assert os.path.exists(os.path.join('.', 'some-cert.crt'))
