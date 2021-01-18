import os

import yaml

from ddb.__main__ import main
from tests.utilstest import expect_gitignore


class TestFilesGenerated:
    def test_ensure_chaining(self, project_loader):
        project_loader("ensure-chaining")

        main(["configure"])

        main(["activate"])

        assert os.path.exists("test.dev.yml.jsonnet")
        assert not os.path.exists("test.dev.yml.jinja")
        with open("test.dev.yml.jsonnet", "r") as dockerfile:
            data = dockerfile.read()
            assert data == '{["e" + "n" + "v"]: "dev"}\n'

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
        assert expect_gitignore('.gitignore', '/test.dev.yml.jsonnet', '/test.dev.yml', '/test.yml')

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
        assert expect_gitignore('.gitignore', '/test.dev.yml.jinja', '/test.dev.yml', '/test.yml')

    def test_directories_overriden(self, project_loader):
        project_loader("directories-overriden")

        assert os.path.isdir("test")

        main(["configure"])

        main(["activate"])

        assert not os.path.isdir("test")
        assert os.path.isfile("test")

    def test_remove_target_on_source_removed(self, project_loader):
        project_loader("remove_target_on_source_removed")

        main(["configure"])

        main(["activate"])

        assert os.path.islink("test")

        os.remove("test.dev")
        os.remove("test2.jinja")

        main(["configure"])

        assert not os.path.exists("test")
        assert not os.path.exists("test2")

    def test_do_not_remove_modified_target_on_source_removed_symlink(self, project_loader):
        project_loader("remove_target_on_source_removed")

        main(["configure"])

        assert os.path.islink("test")
        assert os.path.isfile("test2")

        os.remove("test")
        os.remove("test.dev")
        os.remove("test2.jinja")

        with open("test", "w") as fp:
            fp.write("test")

        main(["configure"])

        assert os.path.exists("test")
        assert not os.path.exists("test2")
