import os
import re
import time

from cfssl import cfssl
from ddb.config import config
from ddb.config.config import ConfigPaths
from ddb.feature.bootstrap import get_sorted_features, bootstrap_features_configuration
from ddb.feature.gitignore import UpdateGitignoreAction


def load_config(data_dir: str = None, name: str = None):
    init_config_paths(data_dir, name)

    bootstrap_features_configuration()
    config.load(config.data)

    return config

def init_config_paths(data_dir: str = None, name: str = None):
    root_dir = os.path.join(data_dir, name) if name else data_dir

    paths = ConfigPaths(ddb_home=os.path.join(root_dir, 'ddb_home'), home=os.path.join(root_dir, 'home'),
                        project_home=os.path.join(root_dir, 'project'))

    if not [path for path in paths if os.path.isdir(path)]:
        paths = ConfigPaths(ddb_home=None, home=None, project_home=root_dir)

    config.paths = paths

    return config


def _get_docker_ip():
    docker_host = os.environ.get('DOCKER_HOST')
    if not docker_host:
        return '127.0.0.1'

    match = re.match(r"tcp:\/\/(.*?):(.*)", docker_host)
    if match:
        return match.group(1)


def _wait_cfssl_ready(max_retry=20):
    client = cfssl.CFSSL(**config.data['certs.cfssl.server'])
    retry = 0
    while True:
        try:
            client.info("")
            break
        except:
            retry += 1
            time.sleep(1)
            if retry > max_retry:
                raise


def setup_cfssl(container_getter):
    cfssl_service = container_getter.get('cfssl')

    config.data['certs.cfssl.server.host'] = _get_docker_ip()
    config.data['certs.cfssl.server.port'] = int(cfssl_service.network_info[0].host_port)
    config.data['certs.cfssl.server.ssl'] = False

    config.defaults.update(config.data)

    _wait_cfssl_ready()


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
