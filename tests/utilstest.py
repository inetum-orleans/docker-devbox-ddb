import os

from ddb.config import config
from ddb.config.config import ConfigPaths


def load_config(data_dir: str = None, name: str = None):
    root_dir = os.path.join(data_dir, name) if name else data_dir

    paths = ConfigPaths(ddb_home=os.path.join(root_dir, 'ddb_home'), home=os.path.join(root_dir, 'home'), project_home=os.path.join(root_dir, 'project'))

    paths = [path for path in paths if os.path.isdir(path)]
    if not paths:
        paths = ConfigPaths(ddb_home=None, home=None, project_home=root_dir)

    config.paths = paths
    config.load()

    return config
