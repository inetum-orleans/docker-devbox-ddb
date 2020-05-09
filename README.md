ddb
===

[![Build Status](https://img.shields.io/travis/gfi-centre-ouest/docker-devbox-ddb.svg)](https://travis-ci.org/gfi-centre-ouest/docker-devbox-ddb)
[![Code coverage](https://img.shields.io/coveralls/github/gfi-centre-ouest/docker-devbox-ddb)](https://coveralls.io/github/gfi-centre-ouest/docker-devbox-ddb)

**[Erase environment differences, make developers happy !](https://gfi-centre-ouest.github.io/docker-devbox-ddb)**

**ddb** automates application configuration so differences between development, staging and production environment can 
be erased. It provides features to generate, activate and adjust configuration files based on a single overridable and
extendable configuration, while enhancing the developer experience and reducing manual operations.

Primarly designed for [docker-compose](https://docs.docker.com/compose/) and [docker-devbox](https://github.com/gfi-centre-ouest/docker-devbox), 
this tool makes the developer forget about the docker hard stuff by providing commands right into it's PATH, so it's 
experience looks like everything is native and locally installed.

Thanks to a pluggable, event based and easy to extend architecture, it can bring powerful configuration automation to 
any technical context.

Install
-------

**ddb** is supported on Linux and Windows. MacOS support is still unsupported, but it should come soon. 

You can [download binary releases on github](https://github.com/gfi-centre-ouest/docker-devbox-ddb/releases), or 
install on Python > 3.5 with pip.

```
pip install docker-devbox-ddb
```

Docs
----

* [How to participate ?](./docs/00-development.md)
* [Changing the default configuration](./docs/10-default_configuration.md)
* [Managing your project configuration](./docs/11-project_configuration.md)

*N.B : Docs are under construction, more will be added over time* 
