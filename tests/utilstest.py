import os
import re

from ddb.config import config
from ddb.config.config import ConfigPaths
from ddb.feature.gitignore import UpdateGitignoreAction


def load_config(data_dir: str = None, name: str = None):
    root_dir = os.path.join(data_dir, name) if name else data_dir

    paths = ConfigPaths(ddb_home=os.path.join(root_dir, 'ddb_home'), home=os.path.join(root_dir, 'home'),
                        project_home=os.path.join(root_dir, 'project'))

    if not [path for path in paths if os.path.isdir(path)]:
        paths = ConfigPaths(ddb_home=None, home=None, project_home=root_dir)

    config.paths = paths
    config.load()

    return config


def get_docker_ip():
    docker_host = os.environ.get('DOCKER_HOST')
    if not docker_host:
        return '127.0.0.1'

    match = re.match(r"tcp:\/\/(.*?):(.*)", docker_host)
    if match:
        return match.group(1)


def expect_gitignore(gitignore: str, *expected_lines: str):
    in_block_lines = set()

    if os.path.exists(gitignore):
        with open(gitignore, 'r') as file:
            inside_block = False
            for gitignore_line in file.read().splitlines():
                if gitignore_line == UpdateGitignoreAction.get_block_limit(True):
                    inside_block = True
                    continue
                if gitignore_line == UpdateGitignoreAction.get_block_limit(False):
                    inside_block = False
                    continue
                if inside_block:
                    in_block_lines.add(gitignore_line)

    for expected_line in expected_lines:
        if expected_line not in in_block_lines:
            return False

    return True
