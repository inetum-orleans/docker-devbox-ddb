# -*- coding: utf-8 -*-
import os

from git import Repo

from ddb.action import Action
from ddb.config import config
from ddb.context import context
from ddb.event import events


class UpdateUmaskAction(Action):
    """
    Update file access rights based on git index
    """

    @property
    def name(self) -> str:
        return "git:update-file-umask"

    @property
    def event_bindings(self):
        return events.phase.configure

    def execute(self):
        """
        Execute the action
        :return:
        """
        if not config.data.get("git.auto_umask"):
            return
        repo = Repo(config.paths.project_home)
        self.process_repository(repo)

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
            UpdateUmaskAction.update_chmod(file_full_path, file_access)

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
        if os.path.isdir(path) or UpdateUmaskAction.is_windows() == 'cmd':
            return

        current_chmod = UpdateUmaskAction.get_current_chmod(path)

        if chmod != '0000' and int(chmod) != int(current_chmod):
            context.log.info("Updating %s umask from %s to %s", path, current_chmod[-4:], chmod[-4:])
            context.log.warning('If this is not expected, update the file umask in git using command "git '
                                'update-index --chmod=+x foo.sh"')
            os.chmod(path, int(chmod[-4:], base=8))

    @staticmethod
    def get_current_chmod(path: str) -> str:
        """
        Retrieve the current chmod for the given path
        :param path: the path to check
        :return:
        """
        return oct(os.lstat(path).st_mode)[-6::]

    @staticmethod
    def is_windows():
        """
        Check if the current system is windows
        :param self:
        :return:
        """
        comspec = os.environ.get('COMSPEC')
        return comspec and comspec.endswith('cmd.exe')
