import os
import shutil

import pytest
from git import Repo

from ddb.__main__ import load_registered_features
from ddb.config import config
from ddb.feature import features
from ddb.feature.core import CoreFeature
from ddb.feature.git import GitFeature, FixFilesPermissionsAction


@pytest.mark.skipif("sys.platform == 'win32'")
class TestGitFixFilesPermissionsAction:

    def test_update_files_disabled(self, project_loader):
        project_loader("disabled")
        features.register(CoreFeature())
        features.register(GitFeature())

        load_registered_features()

        config.data.auto_umask = False

        repo = Repo.init(config.path.project_home)
        repo.git.add('.')
        repo.git.update_index('.gitignore', chmod='+x')
        repo.git.commit('-m "Initial commit"')

        action = FixFilesPermissionsAction()
        action.execute()

        assert action.get_current_chmod(os.path.join(config.path.project_home, '.gitignore')) != '100755'

        shutil.rmtree(config.path.project_home)

    def test_update_files_simple(self, project_loader):
        project_loader("simple")
        features.register(CoreFeature())
        features.register(GitFeature())

        load_registered_features()

        repo = Repo.init(config.path.project_home)
        repo.git.add('.')
        repo.git.update_index('.gitignore', chmod='+x')
        repo.git.commit('-m "Initial commit"')

        action = FixFilesPermissionsAction()
        action.execute()

        assert action.get_current_chmod(os.path.join(config.path.project_home, '.gitignore')) == '100755'

        shutil.rmtree(config.path.project_home)

    def test_update_files_with_submodule(self, project_loader):
        project_loader("with_submodules")
        features.register(CoreFeature())
        features.register(GitFeature())

        load_registered_features()

        path_main = config.path.project_home
        path_submodule = os.path.join(path_main, 'submodule')

        submodule = Repo.init(path_submodule)
        submodule.create_remote('origin', 'https://github.com/gfi-centre-ouest/docker-devbox-ddb')
        submodule.git.add('.')
        submodule.git.update_index('.gitignore', chmod='+x')
        submodule.git.commit('-m "Initial commit"')

        repo = Repo.init(path_main)
        repo.git.add('.')
        repo.create_submodule('a-sub-module', 'submodule', no_checkout=True)
        repo.git.update_index('.gitignore', chmod='+x')
        repo.git.commit('-m "Initial commit"')

        action = FixFilesPermissionsAction()
        action.execute()

        assert FixFilesPermissionsAction.get_current_chmod(os.path.join(config.path.project_home, '.gitignore')) == '100755'
        assert FixFilesPermissionsAction.get_current_chmod(os.path.join(config.path.project_home, '.gitmodules')) == '100644'
        assert FixFilesPermissionsAction.get_current_chmod(
            os.path.join(config.path.project_home, 'submodule', '.gitignore')) == '100755'
