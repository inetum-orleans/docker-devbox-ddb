import os
import time

import cfssl

from ddb.__main__ import load_registered_features
from ddb.config import config
from ddb.feature import features
from ddb.feature.certs import CertsFeature, GenerateCertAction
from ddb.feature.core import CoreFeature


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
        config.data['certs.cfssl.server.host'] = '127.0.0.1'
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
        config.data['certs.cfssl.server.host'] = '127.0.0.1'
        config.data['certs.cfssl.server.port'] = int(cfssl_service.network_info[0].host_port)

        self.wait_cfssl_ready()

        action = GenerateCertAction()
        action.execute(domain="testing.test")

        assert os.path.exists(os.path.join(".certs", "testing.test.crt"))
        assert os.path.exists(os.path.join(".certs", "testing.test.key"))
