from pathlib import Path

import pytest

from ddb.__main__ import load_registered_features, register_actions_in_event_bus
from ddb.feature import features
from ddb.feature.core import CoreFeature
from ddb.feature.feature import FeatureConfigurationError
from ddb.feature.file import FileFeature, FileWalkAction
from ddb.feature.symlinks import SymlinksFeature


class TestSymlinksAction:
    def test_empty_configuration_without_core(self, project_loader):
        project_loader("empty")

        with pytest.raises(FeatureConfigurationError):
            features.register(SymlinksFeature())
            load_registered_features()
            register_actions_in_event_bus(fail_fast=True)

    def test_empty_configuration_with_core(self, project_loader):
        project_loader("empty")

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(SymlinksFeature())
        load_registered_features()
        register_actions_in_event_bus(fail_fast=True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

    def test_project_1(self, project_loader):
        project_loader("project1")

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(SymlinksFeature())
        load_registered_features()
        register_actions_in_event_bus(fail_fast=True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert Path("test").exists()
        assert Path("test").is_symlink()
        assert Path("test").exists()

        assert Path("test.yml").exists()
        assert Path("test.yml").is_symlink()
        assert Path("test.yml").exists()

    def test_project_2_fallback(self, project_loader):
        project_loader("project2")

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(SymlinksFeature())
        load_registered_features()
        register_actions_in_event_bus(fail_fast=True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert Path("test").is_symlink()
        assert str(Path("test").readlink()) == "test.stage"
        assert Path("test").exists()

        assert Path("test.yml").is_symlink()
        assert str(Path("test.yml").readlink()) == "test.dev.yml"
        assert Path("test.yml").exists()

        assert Path("test2").is_symlink()
        assert str(Path("test2").readlink()) == "test2.prod"
        assert Path("test2").exists()

        assert not Path("test3").is_symlink()

    def test_project_4_subdirectory(self, project_loader):
        project_loader("project4")

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(SymlinksFeature())
        load_registered_features()
        register_actions_in_event_bus(fail_fast=True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert (Path("subdirectory") / "test.yml").is_symlink()
        assert str((Path("subdirectory") / "test.yml").readlink()) == "test.dev.yml"

        assert (Path("subdirectory") / "test.yml").exists()

        assert not Path("no.yml").is_symlink()

    def test_project_many_dev(self, project_loader):
        project_loader("project_many_dev")

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(SymlinksFeature())
        load_registered_features()
        register_actions_in_event_bus(fail_fast=True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert Path("test.yml").is_symlink()
        assert str(Path("test.yml").readlink()) == "test.dev.yml"

    def test_project_many_prod(self, project_loader):
        project_loader("project_many_prod")

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(SymlinksFeature())
        load_registered_features()
        register_actions_in_event_bus(fail_fast=True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert Path("test.yml").is_symlink()
        assert str(Path("test.yml").readlink()) == "test.prod.yml"
