import os

from ddb.__main__ import load_registered_features
from ddb.feature import features
from ddb.feature.cookiecutter import CookiecutterFeature
from ddb.feature.cookiecutter.actions import CookiecutterAction


class TestCookiecutterAction:
    def test_empty_project(self, project_loader):
        project_loader("empty")

        features.register(CookiecutterFeature())
        load_registered_features()

        action = CookiecutterAction()
        action.execute()

    def test_github_django(self, project_loader):
        project_loader("github-django")

        features.register(CookiecutterFeature())
        load_registered_features()

        action = CookiecutterAction()
        action.execute()

        assert os.path.isdir('my_awesome_project')
        assert os.path.isfile(os.path.join('my_awesome_project', 'setup.cfg'))
