# -*- coding: utf-8 -*-
import os
import stat

from git import Repo, InvalidGitRepositoryError

from ddb.action import Action
from ddb.config import config
from ddb.context import context
from ddb.event import events


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
            file_access = file_config.split(" ")[0]
            file_full_path = os.path.join(repo.working_dir, file_path)
            FixFilePermissionsAction.update_chmod(file_full_path, file_access)

        for submodule in repo.submodules:
            self.process_repository(submodule.module())

    @staticmethod
    def update_chmod(path, chmod):
        """
        Update the chmod of the file
        :param path: the path to the file
        :param chmod: the chmod to apply
        :return:
        """
        if os.path.isdir(path):
            return

        current_mode = os.stat(path).st_mode
        if chmod[-4:] == '0755' and not os.access(path, os.X_OK):
            context.log.info("Adding execution permission to file %s", path)
            context.log.warning('If this is not expected, update the file permission in git using command "git '
                                'update-index --chmod=+x foo.sh"')
            os.chmod(path, stat.S_IMODE(current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))
            return
        if chmod[-4:] != '0755' and os.access(path, os.X_OK):
            context.log.info("Removing execution permission to file %s", path)
            context.log.warning('If this is not expected, update the file permission in git using command "git '
                                'update-index --chmod=+x foo.sh"')
            os.chmod(path, stat.S_IMODE(current_mode & ~ stat.S_IXUSR & ~ stat.S_IXGRP & ~ stat.S_IXOTH))

    @staticmethod
    def get_current_chmod(path: str) -> str:
        """
        Retrieve the current chmod for the given path
        :param path: the path to check
        :return:
        """
        return oct(os.lstat(path).st_mode)[-6::]
