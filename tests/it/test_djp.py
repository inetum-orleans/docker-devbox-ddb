import os

from ddb.__main__ import main
import zipfile


class TestDjp:
    def test_djp(self, project_loader):
        project_loader("djp")

        with zipfile.ZipFile('template.zip', 'r') as zip_ref:
            zip_ref.extractall('expected')

        main(["download"])

        assert os.path.exists('.docker/djp/Dockerfile.jinja')
        assert os.path.exists('.docker/djp/djp.libjsonnet')

        with open('.docker/djp/djp.libjsonnet') as djp_libjsonnet:
            assert not '// Edited\n' in djp_libjsonnet.readlines()

    def test_djp_patch(self, project_loader):
        project_loader("djp_patch")

        main(["download"])

        assert os.path.exists('.docker/djp/Dockerfile.jinja')
        assert os.path.exists('.docker/djp/djp.libjsonnet')

        with open('.docker/djp/Dockerfile.jinja') as djp_libjsonnet:
            assert 'replaced' not in djp_libjsonnet.read()

        with open('.docker/djp/djp.libjsonnet') as djp_libjsonnet:
            assert '// Edited\n' in djp_libjsonnet.readlines()
