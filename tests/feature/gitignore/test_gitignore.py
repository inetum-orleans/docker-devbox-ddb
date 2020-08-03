import os

from ddb.__main__ import load_registered_features, main
from ddb.feature import features
from ddb.feature.core import CoreFeature
from ddb.feature.gitignore import UpdateGitignoreAction, GitignoreFeature
from tests.utilstest import expect_gitignore


class TestUpdateGitIgnoreAction:
    def test_empty_project_without_core(self, project_loader):
        project_loader("empty")

        features.register(GitignoreFeature())
        load_registered_features()

        action = UpdateGitignoreAction()
        action.execute(target="./to-ignore.yml")
        action.execute(target="./to-ignore-2.yml")

        assert os.path.exists('.gitignore')
        assert expect_gitignore('.gitignore', 'to-ignore.yml', 'to-ignore-2.yml')

    def test_empty_project_with_core(self, project_loader):
        project_loader("empty")

        features.register(CoreFeature())
        features.register(GitignoreFeature())
        load_registered_features()

        action = UpdateGitignoreAction()
        action.execute(target="./to-ignore.yml")

        assert os.path.exists('.gitignore')
        assert expect_gitignore('.gitignore', 'to-ignore.yml')

    def test_already_ignored(self, project_loader):
        project_loader("already_ignored")

        assert os.path.exists('.gitignore')
        with open('.gitignore', 'r') as f:
            expected_gitignore = f.read()

        features.register(GitignoreFeature())
        load_registered_features()

        action = UpdateGitignoreAction()
        action.execute(target="./exists.yml")

        assert os.path.exists('.gitignore')
        with open('.gitignore', 'r') as f:
            gitignore = f.read()

        assert gitignore == expected_gitignore

    def test_keep_negated(self, project_loader):
        project_loader("keep_negated")

        assert os.path.exists('.gitignore')
        with open('.gitignore', 'r') as f:
            expected_gitignore = f.read()

        features.register(GitignoreFeature())
        load_registered_features()

        action = UpdateGitignoreAction()
        action.execute(target="./exists.yml")

        assert os.path.exists('.gitignore')
        with open('.gitignore', 'r') as f:
            gitignore = f.read()

        assert gitignore == expected_gitignore

    def test_templates(self, project_loader):
        project_loader("empty")

        main(["configure"])

        assert os.path.exists(os.path.join('.gitignore'))
        assert expect_gitignore('.gitignore', '*ddb.local.*')

        # TODO faire fonctionner ce test
        # config.data.__setitem__('gitignore.enforce', ['config.txt'])
        # main(["configure"])
        #
        # assert os.path.exists(os.path.join('.gitignore'))
        # assert not expect_gitignore('.gitignore', '*ddb.local.*')
        # assert expect_gitignore('.gitignore', 'config.txt')

