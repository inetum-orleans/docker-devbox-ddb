# -*- coding: utf-8 -*-
import os

import zgitignore

from ddb.action import Action
from ddb.action.action import EventBinding
from ddb.config import config
from ddb.context import context


class UpdateGitignoreAction(Action):
    """
    Append generated files to .gitignore
    """

    @property
    def name(self) -> str:
        return "git:update-gitignore"

    @property
    def event_bindings(self):
        return ("file:generated",
                EventBinding("file:deleted", self.remove))

    @staticmethod
    def find_gitignores(target: str):
        """
        Find writable .gitignore files, walking directories up to project home.
        """
        dirname = target

        while os.path.abspath(dirname) != os.path.abspath(config.paths.project_home):
            dirname = os.path.dirname(dirname)
            gitignore = os.path.join(dirname, ".gitignore")
            if os.path.exists(gitignore) and os.access(gitignore, os.W_OK):
                yield gitignore

    @staticmethod
    def is_file_ignored(file: str, gitignores=None):
        """Check if a file is ignored, going throw all provided gitignore files"""
        if not gitignores:
            gitignores = UpdateGitignoreAction.find_gitignores(file)

        for gitignore in gitignores:
            with open(gitignore, "r", encoding="utf-8") as gitignore_file:
                gitignore_content = gitignore_file.read().splitlines()

            inversed_gitignore_content = []
            for pattern in gitignore_content:
                if pattern.startswith("!"):
                    inversed_gitignore_content.append(pattern[1:])

            relative_file = os.path.normpath(os.path.relpath(file, os.path.dirname(gitignore)))

            zgitignore_helper = zgitignore.ZgitIgnore(gitignore_content)
            inversed_zgitignore_helper = zgitignore.ZgitIgnore(inversed_gitignore_content)
            if zgitignore_helper.is_ignored(relative_file) or inversed_zgitignore_helper.is_ignored(relative_file):
                return True, gitignore, gitignore_content
        return False, None, None

    @staticmethod
    def remove(file: str):
        """
        Remove an ignored file
        :param file:
        :return:
        """
        ignored, gitignore, gitignore_content = UpdateGitignoreAction.is_file_ignored(file)
        if not ignored:
            return

        new_gitignore_content = list(filter(lambda line: file != line, gitignore_content))

        if new_gitignore_content:
            with open(gitignore, "w", encoding="utf-8") as gitignore_file:
                for line in new_gitignore_content:
                    gitignore_file.write(line)
                    gitignore_file.write("\n")
        else:
            os.remove(gitignore)

        context.log.warning("%s removed from %s", file, gitignore)

    @staticmethod
    def execute(target: str, source: str = None):
        """
        Execute action
        """
        gitignores = list(UpdateGitignoreAction.find_gitignores(target))
        if not gitignores:
            gitignores = [".gitignore"]

        for gitignore in gitignores:
            relative_target = os.path.normpath(os.path.relpath(target, os.path.dirname(gitignore)))

            ignored, _, _ = UpdateGitignoreAction.is_file_ignored(relative_target)
            if not ignored:
                last_character = None
                if os.path.exists(gitignore):
                    with open(gitignore, 'rb+') as gitignore_file:
                        gitignore_file.seek(0, 2)
                        size = gitignore_file.tell()
                        if size > 0:
                            gitignore_file.seek(0 - 1, 2)
                            last_character = gitignore_file.read()

                with open(gitignore, "a", encoding="utf-8") as gitignore_file:
                    if last_character and last_character != b"\n":
                        gitignore_file.write("\n")
                    gitignore_file.write(relative_target)
                    gitignore_file.write("\n")
                context.log.success("%s added to %s", relative_target, gitignore)

                return
