import os
import time

import cfssl

from ddb.__main__ import load_registered_features
from ddb.config import config
from ddb.feature import features
from ddb.feature.certs import CertsFeature, GenerateCertAction
from ddb.feature.core import CoreFeature
from tests.utilstest import get_docker_ip


class TestCertsFeature:
    def wait_cfssl_ready(self, max_retry=20):
        client = cfssl.CFSSL(**config.data['certs.cfssl.server'])
        retry = 0
        while True:
            try:
                client.info("")
                break
            except:
                retry += 1
                time.sleep(1)
                if retry > max_retry:
                    raise

    def test_empty_project_without_core(self, project_loader, module_scoped_container_getter):
        project_loader("empty")

        features.register(CertsFeature())
        load_registered_features()

        cfssl_service = module_scoped_container_getter.get('cfssl')

        config.data['certs.cfssl.server.host'] = get_docker_ip()
        config.data['certs.cfssl.server.port'] = int(cfssl_service.network_info[0].host_port)

        self.wait_cfssl_ready()

        action = GenerateCertAction()
        action.execute(domain="testing.test")

        assert os.path.exists(os.path.join(".certs", "testing.test.crt"))
        assert os.path.exists(os.path.join(".certs", "testing.test.key"))

    def test_empty_project_with_core(self, project_loader, module_scoped_container_getter):
        project_loader("empty")

        features.register(CoreFeature())
        features.register(CertsFeature())
        load_registered_features()

        cfssl_service = module_scoped_container_getter.get('cfssl')
        config.data['certs.cfssl.server.host'] = get_docker_ip()
        config.data['certs.cfssl.server.port'] = int(cfssl_service.network_info[0].host_port)

        self.wait_cfssl_ready()

        action = GenerateCertAction()
        action.execute(domain="testing.test")

        assert os.path.exists(os.path.join(".certs", "testing.test.crt"))
        assert os.path.exists(os.path.join(".certs", "testing.test.key"))

        with open(os.path.join(".certs", "testing.test.crt")) as crt_file:
            assert 'CERTIFICATE' in crt_file.read()

        with open(os.path.join(".certs", "testing.test.key")) as key_file:
            assert 'PRIVATE KEY' in key_file.read()

    def test_existing_does_nothing(self, project_loader, module_scoped_container_getter):
        project_loader("existing")

        features.register(CoreFeature())
        features.register(CertsFeature())
        load_registered_features()

        cfssl_service = module_scoped_container_getter.get('cfssl')
        config.data['certs.cfssl.server.host'] = get_docker_ip()
        config.data['certs.cfssl.server.port'] = int(cfssl_service.network_info[0].host_port)

        self.wait_cfssl_ready()

        assert os.path.exists(os.path.join(".certs", "testing.test.crt"))
        assert os.path.exists(os.path.join(".certs", "testing.test.key"))

        with open(os.path.join(".certs", "testing.test.crt")) as crt_file:
            crt = crt_file.read()

        with open(os.path.join(".certs", "testing.test.key")) as key_file:
            key = key_file.read()

        action = GenerateCertAction()
        action.execute(domain="testing.test")

        with open(os.path.join(".certs", "testing.test.crt")) as crt_file:
            assert crt == crt_file.read()

        with open(os.path.join(".certs", "testing.test.key")) as key_file:
            assert key == key_file.read()

