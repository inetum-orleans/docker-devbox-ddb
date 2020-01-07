import os

from ddb.__main__ import load_registered_features
from ddb.context import context
from ddb.feature import features
from ddb.feature.cookiecutter import CookiecutterFeature
from ddb.feature.cookiecutter.actions import ListTagsAction, CookiecutterAction


class TestGigTagsAction:
    def test_empty_project(self, project_loader):
        project_loader("empty")

        features.register(CookiecutterFeature())
        load_registered_features()

        action = ListTagsAction()
        action.execute()

    def test_github_vuejs(self, project_loader):
        project_loader("github-vuejs")

        features.register(CookiecutterFeature())
        load_registered_features()

        action = ListTagsAction()
        action.execute()

        assert 'cookiecutter:list-tags' in context.data
        assert len(context.data['cookiecutter:list-tags']) == 1
        assert 0 in context.data['cookiecutter:list-tags']

        tags = context.data['cookiecutter:list-tags'][0]
        assert 'v2.6.11' in tags


class TestCookiecutterAction:
    def test_github_django(self, project_loader):
        project_loader("github-django")

        features.register(CookiecutterFeature())
        load_registered_features()

        action = CookiecutterAction()
        action.execute()

        assert os.path.isdir('my_awesome_project')
        assert os.path.isfile(os.path.join('my_awesome_project', 'setup.cfg'))
