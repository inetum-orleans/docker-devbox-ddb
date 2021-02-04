from ddb.config import config


def get_mapped_path(path: str):
    """
    Get docker mapped path, using `docker.path_mapping` configuration.
    :param path:
    :return:
    """
    path_mapping = config.data.get('docker.path_mapping')
    fixed_path = None
    fixed_source_path = None
    if path_mapping:
        for source_path, target_path in path_mapping.items():
            if path.startswith(source_path) and \
                    (not fixed_source_path or len(source_path) > len(fixed_source_path)):
                fixed_source_path = source_path
                fixed_path = target_path + path[len(source_path):]
    return fixed_path if fixed_path else path
