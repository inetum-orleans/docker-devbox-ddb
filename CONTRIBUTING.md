## Contribute to docs

You may run the docs locally with docker

```bash
docker run --rm -it -p 8000:8000 --user $(id -u):$(id -g) -v ${PWD}:/docs squidfunk/mkdocs-material serve
```

Docs are then available on http://localhost:8000.

## Publish docs

Create the following file inside `~/.netrc` and replace `<account>` and `<token>` with your github account and personal
access token.

```
machine github.com
login <account>
password <token>

machine api.github.com
login <account>
password <token>

machine uploads.github.com
login <account>
password <token>
```

Github personnal access token can be [here](https://github.com/settings/tokens). (repo must be checked)

```bash
docker run --rm -it -p 8000:8000 --user $(id -u):$(id -g) -v ${PWD}/..:/docs -v ${HOME}/.netrc:/.netrc:ro --workdir=/docs/ddb squidfunk/mkdocs-material gh-deploy
```

## Semantic release and conventional commits

ddb [Changelog](./CHANGELOG.md)
and [released version number](https://github.com/inetum-orleans/docker-devbox-ddb/releases) are automatically
generated from your commit messages using [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/).

Any pull request containing invalid commit messages will be rejected.

Your can use commitizen to help create commit with valid messages.

```bash
cz commit
```

## Configure development environment (Windows)

- Clone this repository and cd into it

You should use [pyenv-win](https://github.com/pyenv-win/pyenv-win) to install and manage your python versions on
Windows.

- Install python 3.8.x

```bash
pyenv install 3.8.7
pyenv local 3.8.7
pyenv rehash
python --version  # Python 3.8.7
```

- Create virtualenv

```bash
python -m venv %USERPROFILE%\.pyenv\pyenv-win\versions\3.8.7-ddb
pyenv local 3.8.7-ddb
pyenv rehash
python --version  # Python 3.8.7
```

- Install dependencies

```bash
pip install -e .[dev]
```

- Enable pre-commit hooks

``bash pre-commit install
``

- Download [ytt](https://get-ytt.io/) binary and make it available in PATH

- Check development version is available in your virtualenv

```
# On windows, use `python -m ddb` instead of ddb only
python -m ddb --version  # Should display a version ending with .dev0
```

- Run tests with pytest

```bash
pytest
```

## Configure development environment (Linux)

You should use [pyenv](https://github.com/pyenv/pyenv) to install and manage your python versions on Linux.

- Clone this repository and cd into it

- Install python 3.8.x

```bash
pyenv install 3.8.7
pyenv local 3.8.7
python --version  # Python 3.8.7
```

- Create virtualenv

```bash
pyenv virtualenv 3.8.7 3.8.7-ddb
pyenv local 3.8.7-ddb
python --version  # Python 3.8.7
```

- Install dependencies

```bash
pip install -e .[dev]
```

- Enable pre-commit hooks

``bash pre-commit install
``

- Download [ytt](https://get-ytt.io/) binary and make it available in PATH

- Check development version is available in your virtualenv

```bash
ddb --version  # Should display a version ending with .dev0
```

- Run tests with pytest

```
pytest
```

## Build and release process

The release process is automated through Github Actions and 
[semantic-release](https://python-semantic-release.readthedocs.io/en/latest/), triggered when pushing to `master`.