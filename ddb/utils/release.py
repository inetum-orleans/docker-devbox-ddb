import requests

ddb_repository = 'gfi-centre-ouest/docker-devbox-ddb'


def get_lastest_release_version():
    """
    Retrieve latest release version from GitHub API
    :return: the json flux from GitHub API
    """
    response = requests.get('https://api.github.com/repos/{}/releases/latest'.format(ddb_repository))
    try:
        response.raise_for_status()
        return response.json().get('tag_name')
    except:  # pylint:disable=bare-except
        return None
