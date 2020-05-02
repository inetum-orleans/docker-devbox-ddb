import os

import yaml

from ddb.__main__ import main
from tests.utilstest import compare_gitignore_generated


class TestFilesGenerated:
    def test_ensure_chaining(self, project_loader):
        project_loader("ensure-chaining")

        main(["configure"])

        main(["activate"])

        assert os.path.exists("test.dev.yml.jsonnet")
        assert not os.path.exists("test.dev.yml.jinja")
        with open("test.dev.yml.jsonnet", "r") as dockerfile:
            data = dockerfile.read()
            assert data == '{["e" + "n" + "v"]: "dev"}'

        assert os.path.exists("test.dev.yml")
        with open("test.dev.yml", "r") as dockerfile:
            data = dockerfile.read()
            assert yaml.load(data, yaml.SafeLoader) == {"env": "dev"}

        assert os.path.exists("test.yml")
        with open("test.yml", "r") as dockerfile:
            data = dockerfile.read()
            assert yaml.load(data, yaml.SafeLoader) == {"env": "dev"}

        assert os.path.islink("test.yml")

        assert os.path.exists(".gitignore")
        with open(".gitignore", "r") as f:
            assert compare_gitignore_generated(f.read(), 'test.dev.yml.jsonnet', 'test.dev.yml', 'test.yml')

    def test_ensure_chaining_with_custom_dependencies(self, project_loader):
        project_loader("ensure-chaining-with-custom-dependencies")

        main(["configure"])

        main(["activate"])

        assert not os.path.exists("test.dev.yml.jsonnet")
        assert os.path.exists("test.dev.yml.jinja")
        with open("test.dev.yml.jinja", "r") as dockerfile:
            data = dockerfile.read().splitlines()
            assert data == ['{', '   "env": "{{ core.env.current }}"', '}']

        assert os.path.exists("test.dev.yml")
        with open("test.dev.yml", "r") as dockerfile:
            data = dockerfile.read()
            assert yaml.load(data, yaml.SafeLoader) == {"env": "dev"}

        assert os.path.exists("test.yml")
        with open("test.yml", "r") as dockerfile:
            data = dockerfile.read()
            assert yaml.load(data, yaml.SafeLoader) == {"env": "dev"}

        assert os.path.islink("test.yml")

        assert os.path.exists(".gitignore")
        with open(".gitignore", "r") as f:
            assert compare_gitignore_generated(f.read(), 'test.dev.yml.jinja', 'test.dev.yml', 'test.yml')
