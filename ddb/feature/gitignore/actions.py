# -*- coding: utf-8 -*-
import os

import zgitignore

from ddb.action import Action
from ddb.config import config
from ddb.context import context


def find_gitignore(target: str):
    """
    Find the nearest writable .gitignore file, walking directories up to project home.
    """
    dirname = target
    while os.path.abspath(dirname) != os.path.abspath(config.paths.project_home):
        dirname = os.path.dirname(dirname)
        gitignore = os.path.join(dirname, ".gitignore")
        if os.path.exists(gitignore) and os.access(gitignore, os.W_OK):
            return gitignore

    return None


class UpdateGitignoreAction(Action):
    """
    Append generated files to .gitignore
    """

    @property
    def name(self) -> str:
        return "git:update-gitignore"

    @property
    def event_bindings(self):
        return "file:generated"

    @staticmethod
    def execute(target: str, source: str = None):
        """
        Execute action
        """
        gitignore = find_gitignore(target)
        if not gitignore:
            gitignore = ".gitignore"
            gitignore_content = []
        else:
            with open(gitignore, "r", encoding="utf-8") as gitignore_file:
                gitignore_content = gitignore_file.read().splitlines()

        inversed_gitignore_content = []
        for pattern in gitignore_content:
            if pattern.startswith("!"):
                inversed_gitignore_content.append(pattern[1:])

        relative_target = os.path.normpath(os.path.relpath(target, os.path.dirname(gitignore)))

        zgitignore_helper = zgitignore.ZgitIgnore(gitignore_content)
        inversed_zgitignore_helper = zgitignore.ZgitIgnore(inversed_gitignore_content)
        if not zgitignore_helper.is_ignored(relative_target) and \
                not inversed_zgitignore_helper.is_ignored(relative_target):
            with open(gitignore, "a", encoding="utf-8") as gitignore_file:
                if gitignore_content and gitignore_content[-1].strip():
                    gitignore_file.write('\n')  # no need for os.linesep because file is opened as text
                gitignore_file.write(relative_target)
            context.log.success("%s added to %s", relative_target, gitignore)
