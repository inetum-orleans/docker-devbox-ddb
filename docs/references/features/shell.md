Shell
===

The shell feature is the one managing the behavior of environment specific behaviors (Windows, Linux/Unix).

For instance, on Linux, shims will be mainly bash executables but on Windows they are .bat files

Feature Configuration
---

- `disabled`: Definition of the status of the feature. If set to True, all SmartCD automations will be disabled.
    - type: boolean
    - default: False
- `aliases`: Allow the creation of aliases available only in ddb projects directories.
    - type: object
    - default: {}
- `envignore`: 
    When activating ddb for a project via `$(ddb activate)`, environment variables are saved before being updated.
    This list is those who will not be saved and updated by the command.
    - type: array
    - default: ["PYENV_*", "_", "PS1", "PS2", "PS3", "PS4"]
- `path.directories`: 
    This list of directories provided is which will be added to the `PATH` environment variable when activating ddb.
    The first one of the list will be the one used as root folder for binaries and aliases shims generation.
    - type: array
    - default: [".bin", "bin"]
- `path.prepend`: This setting define the way `path.directories` are added to the `PATH` environment variable.
    If set to true, it will be added at the beginning.
    - type: boolean
    - default: True
- `shell`: This setting only define what will be the type of shell to work with. Currently, only bash and windows cmd 
    are supported.
    - type: string
    - default: Detect the current shell type used
    
??? example "Configuration example"
    ```yaml
    shell:
      aliases:
        dc: docker-compose
      disabled: false
      envignore:
      - PYENV_*
      - _
      - PS1
      - PS2
      - PS3
      - PS4
      path:
        directories:
        - .bin
        - bin
        prepend: true
      shell: bash
    ```

Environment update
---

ddb is generating configurations for your project and binary management for you docker containers. 

If you have generated binary via using your `docker-compose.yml.jsonnet`, for instance you can run `.bin/psql`.
It means that you need to be in the root folder of your project, or to add the full path to the executable file if you 
are not.

The best solution is to update your `PATH`. 
ddb provides you a simple way to do it by running the following command in your shell :

```
$(ddb activate) 
```

This command will generate environment variables updates commands and execute them, including `PATH` update for easy 
access to executables stored in the `.bin` folder of your project.

!!! info "This environment update is local"
    The modification of the environment variable is local to your current shell session. 
    It means that if you open a new one, the environment will be the same as before run the `$(ddb activate)` command.

** But what happen if you are changing directory and move to another project ?**

The environment variables will still be configured for the project you ran the command for. So before leaving his directory,
you will need to run the following command : 

```
$(ddb deactivate) 
```

It will unload the project specific environment variable configuration and restore it to normal.

Now you can move to the new project directory and run `$(ddb activate)` once again, and so on.

??? info "If you are lazy as we are"
    In order to simplify this process, we implemented a great feature which will automatize it.
    
    For more information, we invite you to check the [SmartCD Feature](smartcd.md)
    

Docker Binary Generation
--- 

If you are using [Jsonnet templates](jsonnet.md) and the `ddb.Binary()` function, this means that you want to have 
simple access to command execution inside docker containers. 

As the generation of the shims depends on your Operating System, it is handled by the shell feature.

Each binary declared will be converted to a simple shims which will be created inside the `shell.path.directories[0]` 
of your project declared in ddb configuration, and available in your shell after running `$(ddb activate)`.

??? example "Access to postgresql command"
    Working with PostgreSQL, you may need to run commands like ...
      - `psql` - PostgreSQL client binary.
      - `pg_dump` - PostgreSQL command line tool to export data to a file.
   
    So, instead of writing a long and boring commmand, you can declare them in your docker-compose.yml.jsonnet as follow:
    ```jsonnet
    local ddb = import 'ddb.docker.libjsonnet';
    
    ddb.Compose() {
        services: {
            db: ddb.Image("postgres") +
                ddb.Binary("psql", "/project", "psql --dbname=postgresql://postgres:ddb@db/postgres") +
                ddb.Binary("pg_dump", "/project", "pg_dump --dbname=postgresql://postgres:ddb@db/postgres") +
              {
                environment+: {POSTGRES_PASSWORD: "ddb"},
                volumes+: [
              'db-data:/var/lib/postgresql/data',
              ddb.path.project + ':/project'
                ]
              }
        }
    }
    ```
    
    Then, run `ddb configure`, which will generate executable files in the `.bin` folder.
    
    Finaly, you can run `$(ddb activate)` to update your `PATH` and bring those commands to your local environment 
    as native ones.
    
    Now, you can run `psql` and `pg_dump` as if they were native commands.

Aliases Management
---

On your environment, aliases can be manually created in order to save time on repetitive commands execution or on long
instructions.
Some of those aliases are really useful only in a specific project context.

The shell feature allows you to create your own aliases which will be generated the same way as 
[docker binaries](#docker-binary-generation) are.

In order to declare them, you need to update the ddb configuration with the list of aliases : 

```yaml
shell:
    aliases:
      myAlias: theLongCommandToExecute
```  

??? example "A long drupal drush path"
    When you are working on drupal project, most of the time [Drush](https://www.drush.org/) command is available 
    globally. But in some case, it is a composer requirement, so it is available through `vendor/drush/drush/drush` path.
    
    So, instead of writing this command each time, you can declare the alias this way: 
    ```yaml
    shell:
      aliases:
        drush: vendor/drush/drush/drush
    ```
    
    A shims will be created and added to the `PATH` thanks to ddb so you will able to use it from you project root folder
    due to the way it is declared : 
    
    ```shell
    drush cr
    ```  