## Contribute to docs

You may run the docs locally with docker

```bash
docker run --rm -it -p 8000:8000 --user $(id -u):$(id -g) -v ${PWD}:/docs squidfunk/mkdocs-material serve
```

Docs are then available on http://localhost:8000.

## Publish docs

Create the following file inside `~/.netrc` and replace `<account>` and `<token>` with your github account and personal access token.

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

## Configure development environment (Windows)

- Clone this repository and cd into it

You should use [pyenv-win](https://github.com/pyenv-win/pyenv-win) to install and manage your python versions on Windows.

- Install python 3.7.x

```
pyenv install 3.7.9
pyenv local 3.7.9
pyenv rehash
python --version  # Python 3.7.9
```

- Create virtualenv

```
python -m venv %USERPROFILE%\.pyenv\pyenv-win\versions\3.7.9-ddb
pyenv local 3.7.9-ddb
pyenv rehash
python --version  # Python 3.7.9
```

- Install dependencies

```
pip install whl/jsonnet-0.15.0-cp37-cp37m-win_amd64.whl
pip install -r requirements-dev.txt
```

- Download [ytt](https://get-ytt.io/) binary and make it available in PATH

- Check development version is available in your virtualenv

```
# On windows, use `python -m ddb` instead of ddb only
python -m ddb --version  # Should display a version ending with .dev0
```

- Run tests with pytest

```
pytest
```

## Configure development environment (Linux)

You should use [pyenv](https://github.com/pyenv/pyenv) to install and manage your python versions on Linux.

- Clone this repository and cd into it

- Install python 3.7.x

```
pyenv install 3.7.9
pyenv local 3.7.9
python --version  # Python 3.7.9
```

- Create virtualenv

```
pyenv virtualenv 3.7.9 3.7.9-ddb
pyenv local 3.7.9-ddb
python --version  # Python 3.7.9
```

- Install dependencies

```
pip install -r requirements-dev.txt
```

- Download [ytt](https://get-ytt.io/) binary and make it available in PATH

- Check development version is available in your virtualenv

```
ddb --version  # Should display a version ending with .dev0
```

- Run tests with pytest

```
pytest
```

## Build and release process

The release process requires docker with custom images of `cdrx/pyinstaller-linux` and `cdrx/pyinstaller-windows`.

A [pull request is opened](https://github.com/cdrx/docker-pyinstaller/pull/90) and I hope it will be merged soon.

Those custom images are available on Docker Hub under `toilal/pyinstaller-linux` and `toilal/pyinstaller-windows` repositories.

```
prerelease

rm -Rf dist/ &&\
python setup.py clean build bdist bdist_wheel bdist_pex --pex-args="--disable-cache" --bdist-all &&\
docker run --rm --init -v "$(pwd):/src/" -e "DISABLE_REQUIREMENTS=1" toilal/pyinstaller-linux:xenial "pip install --upgrade setuptools && pip install -r requirements.txt && pyinstaller --clean -y --dist ./dist --workpath /tmp *.spec" &&\
docker run --rm --init -v "$(pwd):/src/" -e "DISABLE_REQUIREMENTS=1" toilal/pyinstaller-windows "pip install --upgrade setuptools && pip install whl/jsonnet-0.15.0-cp37-cp37m-win_amd64.whl && pip install -r requirements.txt && pyinstaller --clean -y --dist ./dist --workpath /tmp *.spec"

release

githubrelease release gfi-centre-ouest/docker-devbox-ddb create $(python -m ddb --version -s) --name $(python -m ddb --version -s) --publish "dist/*"

postrelease
```

