import os

import pytest

from ddb.__main__ import load_registered_features
from ddb.feature import features
from ddb.feature.core import CoreFeature
from ddb.feature.feature import FeatureConfigurationError
from ddb.feature.symlinks import ConfigureAction, SymlinksFeature


class TestConfigureAction:
    def test_empty_configuration_without_core(self):
        with pytest.raises(FeatureConfigurationError):
            features.register(SymlinksFeature())
            load_registered_features()

    def test_empty_configuration_with_core(self):
        features.register(CoreFeature())
        features.register(SymlinksFeature())
        load_registered_features()

        action = ConfigureAction()
        action.execute()

    def test_project_1(self, project_loader):
        project_loader("project1")

        features.register(CoreFeature())
        features.register(SymlinksFeature())
        load_registered_features()

        action = ConfigureAction()
        action.execute()

        assert os.path.exists('test')
        assert os.path.islink('test')

        assert os.path.exists('test.yml')
        assert os.path.islink('test.yml')

    def test_project_2_fallback(self, project_loader):
        project_loader("project2")

        features.register(CoreFeature())
        features.register(SymlinksFeature())
        load_registered_features()

        action = ConfigureAction()
        action.execute()

        assert os.path.islink('test')
        assert os.readlink('test') == 'test.stage'

        assert os.path.islink('test.yml')
        assert os.readlink('test.yml') == 'test.dev.yml'

        assert os.path.islink('test2')
        assert os.readlink('test2') == 'test2.prod'

        assert not os.path.islink('test3')

    def test_project_3_missing(self, project_loader):
        project_loader("project3")

        features.register(CoreFeature())
        features.register(SymlinksFeature())
        load_registered_features()

        action = ConfigureAction()
        action.execute()

    def test_project_4_subdirectory(self, project_loader):
        project_loader("project4")

        features.register(CoreFeature())
        features.register(SymlinksFeature())
        load_registered_features()

        action = ConfigureAction()
        action.execute()

        assert os.path.islink(os.path.join('subdirectory', 'test.yml'))
        assert os.readlink(os.path.join('subdirectory', 'test.yml')) == 'subdirectory/test.dev.yml'

        assert not os.path.islink('no.yml')
