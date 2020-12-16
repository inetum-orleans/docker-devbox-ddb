import requests

ddb_repository = 'gfi-centre-ouest/docker-devbox-ddb'


def get_latest_release_version():
    """
    Retrieve latest release version from GitHub API
    :return: Version from tag_name retrieved from GitHub API
    """
    response = requests.get('https://api.github.com/repos/{}/releases/latest'.format(ddb_repository))
    try:
        response.raise_for_status()
        tag_name = response.json().get('tag_name')
        if tag_name and tag_name.startswith('v'):
            tag_name = tag_name[1:]
        return tag_name
    except:  # pylint:disable=bare-except
        return None
