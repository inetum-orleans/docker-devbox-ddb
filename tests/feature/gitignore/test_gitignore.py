import os

from ddb.__main__ import load_registered_features, main
from ddb.feature import features
from ddb.feature.core import CoreFeature
from ddb.feature.gitignore import UpdateGitignoreAction, GitignoreFeature


class TestUpdateGitIgnoreAction:
    def test_empty_project_without_core(self, project_loader):
        project_loader("empty")

        features.register(GitignoreFeature())
        load_registered_features()

        action = UpdateGitignoreAction()
        action.execute(target="./to-ignore.yml")
        action.execute(target="./to-ignore-2.yml")

        assert os.path.exists('.gitignore')
        with open('.gitignore', 'r') as f:
            gitignore = f.read()

        assert gitignore == ('\n'.join([
            UpdateGitignoreAction.get_block_limit(True),
            'to-ignore.yml',
            'to-ignore-2.yml',
            UpdateGitignoreAction.get_block_limit(False),
        ]) + '\n')

    def test_empty_project_with_core(self, project_loader):
        project_loader("empty")

        features.register(CoreFeature())
        features.register(GitignoreFeature())
        load_registered_features()

        action = UpdateGitignoreAction()
        action.execute(target="./to-ignore.yml")

        assert os.path.exists('.gitignore')
        with open('.gitignore', 'r') as f:
            gitignore = f.read()

        assert gitignore == ('\n'.join([
            UpdateGitignoreAction.get_block_limit(True),
            'to-ignore.yml',
            UpdateGitignoreAction.get_block_limit(False),
        ]) + '\n')

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
        project_loader("templates")

        main(["configure"])

        assert os.path.exists(os.path.join('.gitignore'))
        with open(os.path.join('.gitignore'), 'r') as f:
            gitignore = f.read()
            assert gitignore == ('\n'.join([
                UpdateGitignoreAction.get_block_limit(True),
                'no/gitignore/directory/foo.txt',
                UpdateGitignoreAction.get_block_limit(False),
            ]) + '\n')

        assert os.path.exists(os.path.join('sub', '.gitignore'))
        with open(os.path.join('sub', '.gitignore'), 'r') as f:
            gitignore = f.read()
            assert gitignore == ('\n'.join([
                UpdateGitignoreAction.get_block_limit(True),
                'directory/test.json',
                'directory/test.yaml',
                UpdateGitignoreAction.get_block_limit(False),
            ]) + '\n')

        assert os.path.exists(os.path.join('another', 'sub', '.gitignore'))
        with open(os.path.join('another', 'sub', '.gitignore'), 'r') as f:
            gitignore = f.read()
            assert gitignore == '\n'.join([
                'foo',
                '!directory/forced.*',
                'bar',
            ])

        assert os.path.exists(os.path.join('another', 'sub', 'directory', '.gitignore'))
        with open(os.path.join('another', 'sub', 'directory', '.gitignore'), 'r') as f:
            gitignore = f.read()
            assert gitignore == ('\n'.join([
                UpdateGitignoreAction.get_block_limit(True),
                'test.yaml',
                UpdateGitignoreAction.get_block_limit(False),
            ]) + '\n')
