import os
import shutil

import pytest
from git import Repo

from ddb.__main__ import load_registered_features
from ddb.config import config
from ddb.feature import features
from ddb.feature.core import CoreFeature
from ddb.feature.git import GitFeature, FixFilePermissionsAction


def test_update_files_disabled(project_loader):
    project_loader("disabled")
    features.register(CoreFeature())
    features.register(GitFeature())

    load_registered_features()

    config.data['git.fix_file_permissions'] = False

    action = FixFilePermissionsAction()
    assert action.disabled is True


@pytest.mark.skipif("os.name == 'nt'")
class TestGitFixFilesPermissionsAction:
    def test_update_files_simple(self, project_loader):
        project_loader("simple")
        features.register(CoreFeature())
        features.register(GitFeature())

        load_registered_features()

        repo = Repo.init(config.path.project_home)
        repo.git.add('.')
        repo.git.update_index('.gitignore', chmod='+x')
        repo.git.commit('-m "Initial commit"')

        action = FixFilePermissionsAction()
        action.execute()

        assert os.access(os.path.join(config.path.project_home, '.gitignore'), os.X_OK)

        shutil.rmtree(config.path.project_home)

    def test_update_files_with_submodule(self, project_loader):
        project_loader("with_submodules")
        features.register(CoreFeature())
        features.register(GitFeature())

        load_registered_features()

        path_main = config.path.project_home
        path_submodule = os.path.join(path_main, 'submodule')

        submodule = Repo.init(path_submodule)
        submodule.create_remote('origin', 'https://github.com/inetum-orleans/docker-devbox-ddb')
        submodule.git.add('.')
        submodule.git.update_index('.gitignore', chmod='+x')
        submodule.git.commit('-m "Initial commit"')

        repo = Repo.init(path_main)
        repo.git.add('.')
        repo.create_submodule('a-sub-module', 'submodule', no_checkout=True)
        repo.git.update_index('.gitignore', chmod='+x')
        repo.git.commit('-m "Initial commit"')

        action = FixFilePermissionsAction()
        action.execute()

        assert os.access(os.path.join(config.path.project_home, '.gitignore'), os.X_OK)
        assert os.access(os.path.join(config.path.project_home, 'submodule', '.gitignore'), os.X_OK)
        assert not os.access(os.path.join(config.path.project_home, '.gitmodules'), os.X_OK)
