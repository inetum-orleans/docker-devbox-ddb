Binaries
===

a typical ddb project is configured to **register binaries inside the environment**.

Most often, binaries are registered inside `docker-compose.yml.jsonnet` using
[ddb.Binary()](./features/jsonnet.md#ddbbinary).

Docker binary shims **are available in the shell `PATH`** and acts as aliases to binaries living in images or containers of
docker-compose services. They delegate to [ddb run command](./commands.md#ddb-run) to generate a complex
`docker-compose run` or `docker-compose exec` command to invoke. 

Those binaries **let you think they are locally installed** on your computer, but everything still runs inside docker.
This is because ddb take cares of **common docker pitfalls** : project and current working directory are mapped properly, 
host shell is integrated and permission issues are solved thanks to [fixuid feature](./features/fixuid.md).

Binary shims are created inside `.bin` directory of the project on
[ddb configure command](./commands.md#ddb-configure) to be registered in the shell `PATH` during
[ddb activate command](./commands.md#ddb-activate).

**Binaries can also be registered globally**, using [ddb.Binary(..., global=true)](./features/jsonnet.md#ddbbinary). 
Those binaries are then available from any directory. It can be handy to register some global tools using a ddb 
project as a way to package it.

Binaries can also be registered through [shell feature Aliases Management](./features/shell.md#aliases-management).

!!! info "Customize docker-compose run options for docker binaries"
    You can customize docker-compose run options by using `DDB_RUN_OPTS` environment variable. It can be used define 
    environment variables to the container running the binary using docker-compose `-e` flag.

    ```shell
    # To run phpunit with code coverage, XDEBUG_MODE environment variable has to be set to "coverage"
    DDB_RUN_OPTS="-e XDEBUG_MODE=coverage" bin/phpunit
    ```
