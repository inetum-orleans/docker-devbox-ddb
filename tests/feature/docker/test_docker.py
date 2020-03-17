import os

from ddb.__main__ import load_registered_features
from ddb.feature import features
from ddb.feature.docker import DockerFeature, CopyToBuildContextAction


class TestUpdateGitIgnoreAction:
    def test_empty_project_without_core(self, project_loader):
        project_loader("copy-ca-certificates")

        features.register(DockerFeature())
        load_registered_features()

        action = CopyToBuildContextAction()
        action.execute()

        assert os.path.exists(os.path.join('.docker', 'service1', 'ca-certs', 'some-cert.crt'))
        assert not os.path.exists(os.path.join('.docker', 'service1', 'ca-certs', 'another-cert.crt'))

        assert os.path.exists(os.path.join('.docker', 'service2', 'ca-certs', 'some-cert.crt'))
        assert not os.path.exists(os.path.join('.docker', 'service2', 'ca-certs', 'another-cert.crt'))

        assert not os.path.exists(os.path.join('.docker', '.not-a-service', 'ca-certs', 'some-cert.crt'))
        assert not os.path.exists(os.path.join('.docker', '.not-a-service', 'ca-certs', 'another-cert.crt'))
