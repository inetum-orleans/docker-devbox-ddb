Frequently Asked Questions
===

??? question "How to customize the configuration for a single project ?"
    You may create a `ddb.local.yml` configuration file in the project directory.
    
    Read more: [Configuration](configuration.md)
    
??? question "How to customize the configuration for all project on the host ?"
    You may create a `ddb.yml` configuration file in the `~/.docker-devbox` installation directory or in your home folder.
    
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
    
    You can override `core.domain.ext` setting globally by creating a `ddb.local.yml` file in `~/.docker-devbox` installation directory or in your home folder.
    
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

??? question "ddb fails to run with message: `version 'GLIBC_2.35' not found`"

    It seems you are running an old, unsupported linux distribution, like Ubuntu 16.04.

    Currently, ddb works on ubuntu 22.04 or equivalent, using glibc 2.35 or higher.
    You may also have luck installing ddb from pip if your distribution can run a supported python version.

??? question "What to do in case of a `ddb self-update` failure ?"
    Starting from version 3.1.0, ddb creates a `ddb.old` backup file in the installation directory
    (usually `~/.docker-devbox/bin`), before upgrading to a higher version.
    
    You can restore it by running the following command:

    ```bash
    mv ~/.docker-devbox/bin/ddb.old ~/.docker-devbox/bin/ddb
    ```

    Otherwise you may also install a specific version of ddb by using the command below:

    ```bash
    curl -L -o ~/.docker-devbox/bin/ddb https://github.com/inetum-orleans/docker-devbox-ddb/releases/download/v3.0.2/ddb-linux && chmod +x ~/.docker-devbox/bin/ddb
    ```

    You may also download one of the release from the
    [github release page](https://github.com/inetum-orleans/docker-devbox-ddb/releases) manually and place it in the installation directory.
