import os

from ddb.__main__ import main


class TestJsonnet:
    def test_jsonnet_ext_var(self, project_loader):
        project_loader("jsonnet-extvar")

        main(["configure"])

        assert os.path.exists('config.yml')
        with open('config.yml', 'r') as f:
            variables = f.read()

        with open('config.expected.yml', 'r') as f:
            variables_expected = f.read()

        assert variables == variables_expected
