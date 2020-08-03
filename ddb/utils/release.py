import requests

ddb_repository = 'gfi-centre-ouest/docker-devbox-ddb'


def get_last_release():
    """
    Retrieve latest release information from GitHub API
    :return: the json flux from GitHub API
    """
    response = requests.get('https://api.github.com/repos/{}/releases/latest'.format(ddb_repository))
    return response.json()
