Run
===

As **ddb** is a way to simplify the way to work with docker, this feature is a very useful one. 

If you are working with the [jsonnet](./jsonnet.md) feature and the [Binary](./jsonnet.md#binary) function in your 
docker-compose.yml.jsonnet, the `run` feature will allow you to run commands in your docker container just as if it 
was a native system command.

Feature Configuration
---

There is only one configuration available for this feature : 

- `disabled`: Definition of the status of the feature. If set to True, this feature will not be available.
    - type: boolean
    - default: False
    
!!! example "Configuration"
    ```yaml
    run:
        disabled: false
    ```
     
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

!!! example "How to use npm natively ?"
    If you follow the [Guide for PostgreSQL, Symfony, VueJS](../guides/psql-symfony-vue.md), you will be able to execute
    `ddb run npm` which will output the following command `docker-compose run --rm --workdir=/app/. node npm`.
    
    But, as explained, ddb will also create a binary for npm that you will be able to run as a native command, which is 
    far more easy to use for everyone.