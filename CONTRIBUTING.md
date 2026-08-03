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
uv run cz commit
```

## Configure development environment

Dependencies and virtualenvs are managed with [uv](https://docs.astral.sh/uv/), which also downloads the
python interpreter when needed. ddb supports python 3.11 to 3.14.

- Clone this repository and cd into it

- Install dependencies (creates `.venv` from `uv.lock`)

```bash
uv sync
```

- Enable pre-commit hooks

```bash
uv run pre-commit install
```

- Download [ytt](https://carvel.dev/ytt/) binary and make it available in PATH

- Check development version is available

```bash
uv run ddb --version
```

- Run tests with pytest

```bash
uv run pytest
```

- Run the quality gate (ruff check and format, as in CI)

```bash
uv run pre-commit run --all-files
```

- Run the test suite against every supported python version

```bash
uv run tox
```

## Build and release process

The release process is automated through Github Actions and
[semantic-release](https://python-semantic-release.readthedocs.io/en/latest/), triggered when pushing to `master`.

The standalone binary can be built locally with pyinstaller.

```bash
uv run pyinstaller --dist ./dist ddb.spec
```
