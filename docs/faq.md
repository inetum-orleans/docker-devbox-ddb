Frequently Asked Questions
===

??? question "How to customize the configuration for a single project ?"
    You may create a `ddb.local.yml` configuration file in the project directory.
    
    Read more: [Configuration](configuration.md)
    
??? question "How to customize the configuration for all project on the host ?"
    You may create a `ddb.yml` configuration file in the `~/.docker-devbox` installation directory.
    
    You can also add environment variable matching the property name to override, in UPPERCASE, prefixed 
    with `DDB_` and `.` replaced with `_`.
    
    Read more: [Configuration](configuration.md)

??? question "How to change the domain name for a single project ?"
    Domain name is configured through 2 `core` settings.
    
        core.domain.ext: test
        core.domain.sub: folder
    
    Those settings are joined with `.` to build the main domain name (`folder.test`).
    
    Read more: [Configuration](configuration.md)
    
??? question "How to change the domain extension for all projects ?"
    Domain name is configured through 2 `core` settings.
    
        core.domain.ext: test
        core.domain.sub: folder
    
    Those settings are joined with `.`, `folder.test` to build the main domain name.
    
    You can override `core.domain.ext` setting globally by creating a `ddb.local.yml` file in `~/.docker-devbox` installation directory.
    
    You can also define a system environment variable named `DDB_CORE_DOMAIN_EXT` with the domain extension.
    
    Read more: [Configuration](configuration.md)
    
??? question "How to disable/enable tags from docker images defined in generated docker-compose.yml file ?"
    In your project `ddb.yml` file, you may disable this option in the [jsonnet feature](./features/jsonnet.md) 
    with `jsonnet.docker.build.image_tag_from` set to false.
    
    Read more: [Configuration](configuration.md)
    
??? question "CI fails with the following message: "the input device is not a TTY""

    If no TTY is available, you have to set the following environment variable to workaround this issue

    COMPOSE_INTERACTIVE_NO_CLI=1

??? question "How to clear cache ?"

    Run `ddb --clear-cache configure` or `rm -Rf ~/.docker-devbox/cache`.

??? question "ddb fails to run with message: `version 'GLIBC_2.25' not found`"

    It seems you are running an old linux distribution, like Ubuntu 16.04.

    You should either install ddb from pip, or use `ddb-linux-older-glic` binary from 
    [github release page](https://github.com/inetum-orleans/docker-devbox-ddb/releases).

    Then set `core.release_asset_name: ddb-linux-older-glic` inside your ddb configuration (`~/.docker-devbox/ddb.yml`)
    to make `ddb self-update` download this edition.


