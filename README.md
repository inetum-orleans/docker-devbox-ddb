ddb
===

[![PyPI](https://img.shields.io/pypi/v/docker-devbox-ddb)](https://pypi.org/project/docker-devbox-ddb/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/docker-devbox-ddb)](https://pypi.org/project/docker-devbox-ddb/)
[![PyPI - License](https://img.shields.io/pypi/l/docker-devbox-ddb)](https://github.com/inetum-orleans/docker-devbox-ddb/blob/develop/LICENSE)
[![Build Status](https://github.com/inetum-orleans/docker-devbox-ddb/workflows/build/badge.svg)](https://github.com/inetum-orleans/docker-devbox-ddb/actions?query=workflow%3Abuild)
[![Code coverage](https://img.shields.io/codecov/c/github/inetum-orleans/docker-devbox-ddb)](https://app.codecov.io/gh/inetum-orleans/docker-devbox-ddb)
[![semantic-release](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--release-e10079.svg)](https://github.com/relekang/python-semantic-release)

**[Erase environment differences, make developers happy !](https://inetum-orleans.github.io/docker-devbox-ddb)**

**ddb** automates application configuration so differences between development, staging and production environment can 
be erased. It provides features to generate, activate and adjust configuration files based on a single overridable and
extendable configuration, while enhancing the developer experience and reducing manual operations.

Primarly designed for [docker-compose](https://docs.docker.com/compose/) and [docker-devbox](https://github.com/inetum-orleans/docker-devbox), 
this tool makes the developer forget about the docker hard stuff by providing commands right into it's PATH, so it's 
experience looks like everything is native and locally installed.

Thanks to a pluggable, event based and easy to extend architecture, it can bring powerful configuration automation to 
any technical context.

Install
-------

**ddb** is supported on Linux and Windows. MacOS is still unsupported, but it should come soon. 

You can [download binary releases on github](https://github.com/inetum-orleans/docker-devbox-ddb/releases), or 
install on Python >= 3.5 with pip.

```
pip install docker-devbox-ddb
```

Docs
----

[Documentation is available here](https://inetum-orleans.github.io/docker-devbox-ddb)
