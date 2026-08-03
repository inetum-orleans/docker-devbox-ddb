from pathlib import Path

import yaml

from ddb.__main__ import main
from tests.utilstest import expect_gitignore


class TestFilesGenerated:
    def test_ensure_chaining(self, project_loader):
        project_loader("ensure-chaining")

        main(["configure"])

        main(["activate"])

        assert Path("test.dev.yml.jsonnet").exists()
        assert not Path("test.dev.yml.jinja").exists()
        with Path("test.dev.yml.jsonnet").open() as dockerfile:
            data = dockerfile.read()
            assert data == '{["e" + "n" + "v"]: "dev"}\n'

        assert Path("test.dev.yml").exists()
        with Path("test.dev.yml").open() as dockerfile:
            data = dockerfile.read()
            assert yaml.load(data, yaml.SafeLoader) == {"env": "dev"}

        assert Path("test.yml").exists()
        with Path("test.yml").open() as dockerfile:
            data = dockerfile.read()
            assert yaml.load(data, yaml.SafeLoader) == {"env": "dev"}

        assert Path("test.yml").is_symlink()

        assert Path(".gitignore").exists()
        assert expect_gitignore(".gitignore", "/test.dev.yml.jsonnet", "/test.dev.yml", "/test.yml")

    def test_ensure_chaining_with_custom_dependencies(self, project_loader):
        project_loader("ensure-chaining-with-custom-dependencies")

        main(["configure"])

        main(["activate"])

        assert not Path("test.dev.yml.jsonnet").exists()
        assert Path("test.dev.yml.jinja").exists()
        with Path("test.dev.yml.jinja").open() as dockerfile:
            data = dockerfile.read().splitlines()
            assert data == ["{", '   "env": "{{ core.env.current }}"', "}"]

        assert Path("test.dev.yml").exists()
        with Path("test.dev.yml").open() as dockerfile:
            data = dockerfile.read()
            assert yaml.load(data, yaml.SafeLoader) == {"env": "dev"}

        assert Path("test.yml").exists()
        with Path("test.yml").open() as dockerfile:
            data = dockerfile.read()
            assert yaml.load(data, yaml.SafeLoader) == {"env": "dev"}

        assert Path("test.yml").is_symlink()

        assert Path(".gitignore").exists()
        assert expect_gitignore(".gitignore", "/test.dev.yml.jinja", "/test.dev.yml", "/test.yml")

    def test_directories_overriden(self, project_loader):
        project_loader("directories-overriden")

        assert Path("test").is_dir()

        main(["configure"])

        main(["activate"])

        assert not Path("test").is_dir()
        assert Path("test").is_file()

    def test_remove_target_on_source_removed(self, project_loader):
        project_loader("remove_target_on_source_removed")

        main(["configure"])

        main(["activate"])

        assert Path("test").is_symlink()

        Path("test.dev").unlink()
        Path("test2.jinja").unlink()

        main(["configure"])

        assert not Path("test").exists()
        assert not Path("test2").exists()

    def test_do_not_remove_modified_target_on_source_removed_symlink(self, project_loader):
        project_loader("remove_target_on_source_removed")

        main(["configure"])

        assert Path("test").is_symlink()
        assert Path("test2").is_file()

        Path("test").unlink()
        Path("test.dev").unlink()
        Path("test2.jinja").unlink()

        with Path("test").open("w") as fp:
            fp.write("test")

        main(["configure"])

        assert Path("test").exists()
        assert not Path("test2").exists()
