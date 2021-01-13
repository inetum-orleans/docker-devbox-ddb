# -*- coding: utf-8 -*-
import os

from git import Repo, InvalidGitRepositoryError

from ddb.action import Action
from ddb.config import config
from ddb.context import context
from ddb.event import events
from ddb.utils.file import chmod


class FixFilePermissionsAction(Action):
    """
    Update file access permissions based on git index
    """

    @property
    def name(self) -> str:
        return "git:fix-file-permissions"

    @property
    def event_bindings(self):
        return events.phase.configure

    @property
    def disabled(self) -> bool:
        return not config.data.get("git.fix_files_permissions") or os.name == 'nt'

    def execute(self):
        """
        Execute the action
        :return:
        """
        try:
            repo = Repo(config.paths.project_home)
            self.process_repository(repo)
        except InvalidGitRepositoryError:
            pass

    def process_repository(self, repo: Repo):
        """
        Process a repository
        :param repo: the repository to process
        :return:
        """
        for file_data in repo.git.ls_files(s=True).splitlines():
            file_config, file_path = file_data.split("\t")
            git_mode = file_config.split(" ")[0]
            file_full_path = os.path.join(repo.working_dir, file_path)
            FixFilePermissionsAction.update_mode(file_full_path, git_mode)

        for submodule in repo.submodules:
            self.process_repository(submodule.module())

    @staticmethod
    def update_mode(path, git_mode):
        """
        Update the chmod of the file
        :param path: the path to the file
        :param git_mode: the chmod to apply
        :return:
        """
        if os.path.isdir(path):
            return

        if git_mode[-4:] == '0755' and not os.access(path, os.X_OK):
            chmod(path, '+x')
            context.log.warning('If this chmod is not expected, update the file permission in git using command "git '
                                'update-index --chmod=+x foo.sh"')
            return

        if git_mode[-4:] != '0755' and os.access(path, os.X_OK):
            chmod(path, '-x')
            context.log.warning('If this chmod is not expected, update the file permission in git using command "git '
                                'update-index --chmod=+x foo.sh"')

    @staticmethod
    def get_current_chmod(path: str) -> str:
        """
        Retrieve the current chmod for the given path
        :param path: the path to check
        :return:
        """
        return oct(os.lstat(path).st_mode)[-6::]
