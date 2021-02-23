Run
===

As **ddb** is a way to simplify the way to work with docker, this feature is a very useful one. 

If you are working with the [jsonnet](./jsonnet.md) feature and the [Binary](./jsonnet.md#ddbbinary) function in your 
`docker-compose.yml.jsonnet`, `run` feature allow you to run commands in your docker container just as if it 
was a native system command.

!!! summary "Feature configuration (prefixed with `run.`)"
    | Property | Type | Description |
    | :---------: | :----: | :----------- |
    | `disabled` | boolean<br>`false` | Should this feature be disabled ? |

Run command in container as if it was native
---

As said in introduction, the purpose of the `run` feature is to allow you to run commands in your docker container 
just as if it was a native system command.

In order to do so, the feature will look in the project configuration for the binary you are trying to run. Then, it 
will generate the right docker-compose command to be executed.

But, as we are lazy, it was not enough. 
So, when you create a project  the [docker](./docker.md) will trigger the [shell](./shell.md) one, which will generate a 
binary file for the current project. This file will simply execute the `ddb run <binary_name>` with the input argument 
and automatically execute the result.

The combination of the previously named feature with the current one will grant you the capability to execute `npm` just
as you would do with a system installation of it.

!!! question "How to run `npm` or `composer` command ?"
    If you follow the [Guide for PostgreSQL, Symfony, VueJS](../guides/psql-symfony-vue.md), you will be able to execute
    `ddb run npm` which will output the following command `docker-compose run --rm --workdir=/app/. node npm`.
    
    But, as explained, ddb will also create a binary shim for npm so you can run it like a native command, which is 
    far more easy to use for everyone. Run $(ddb activate), and then `npm` is available right in your shell path.

Register many binaries for the same command
---

When a binary shim is invoked, it runs `ddb run <command-name>` under the hood.

All declared binaries matching the command name with a `condition` defined will have their `condition` evaluated, and 
the first one returning `True` is used to generate the effective command output. 

If no `condition` match, the first remaining one is used.

If no binary is finally found, the command is wrapped into equivalent of `$(ddb deactivate)`/`$(ddb activate)`
instruction so it runs on the host system.
