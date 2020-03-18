docker-devbox-ddb
=================
[![Build Status](https://img.shields.io/travis/gfi-centre-ouest/docker-devbox-ddb.svg)](https://travis-ci.org/gfi-centre-ouest/docker-devbox-ddb)
[![Code coverage](https://img.shields.io/coveralls/github/gfi-centre-ouest/docker-devbox-ddb)](https://coveralls.io/github/gfi-centre-ouest/docker-devbox-ddb)

Development
-----------

- Create virtualenv from Python `3.5.x`.

You should consider [pyenv](https://github.com/pyenv/pyenv) or [pyenv-win](https://github.com/pyenv-win/pyenv-win).

```
pyenv install 3.5.9
pyenv rehash
python -m venv ~/.pyenv/versions/3.5.9-ddb
pyenv local 3.5.9-ddb
```

- Install development dependencies

```
pip install -r requirements-dev.txt
```

- Run pytest

```
pytest
```

- Run pylint

```
pylint ddb
```

### Windows note

If you are running Windows, you need to follow those steps ...

- Install [Build Tools for Visual Studio 2019](https://visualstudio.microsoft.com/thank-you-downloading-visual-studio/?sku=BuildTools&rel=16), 
and choose Windows 10 SDK, C++ Build Tools and C++ CMake Tools for Windows in installer (last version only).
- Install jsonnet python extension from [Toilal/jsonnet](https://github.com/Toilal/jsonnet) fork (this fix windows build)

```
pip install git+https://github.com/Toilal/jsonnet.git#egg=jsonnet
```
