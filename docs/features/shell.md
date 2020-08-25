Shell
===

The shell feature manages OS/Shell specific behaviors (Windows, Linux/Unix).

For instance, generated binary shims are bash executables on Linux, but .bat files on Windows.

Feature Configuration
---

- `disabled`: Definition of the status of the feature. If set to True, all SmartCD automations will be disabled.
    - type: boolean
    - default: False
- `aliases`: Allow the creation of aliases.
    - type: dict[str, str]
    - default: {}
- `global_aliases`: For aliases matching those names, aliases will be declared globally instead of inside project only.
    - type: array
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
    
!!! example "Configuration"
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

Environment activation
---

ddb is generating configurations for your project and brings docker container binaries right in your development 
environment. 

If you have registered binary inside `docker-compose.yml.jsonnet`, you can found binary shims inside `.bin` directory.
It means that you need to be in the root folder of your project, or to add the full path to the executable file if you 
are not.

The best solution is to update your `PATH`. ddb provides you a way to do it by running the `$(ddb activate)` command in your shell.

This command will generate environment variables updates commands and execute them, including `PATH` update for easy 
to access stored in the `.bin` folder of your project from anywhere.

!!! info "Changes to environment are local and not persistent"
    The modification of the shell environment is local to your current shell session. 
    It means that if you open a new one, the environment will be the same as before run the `$(ddb activate)` command.

!!! question "But what happen when switching to another project ?"
    The environment variables will still be configured for the project you ran the command for. So before leaving his directory,
    you will need to run `$(ddb deactivate) ` command.

    It will unload the project specific environment variable configuration and restore it to the initial state.
    
    Now you can move to the new project directory and run `$(ddb activate)` once again, and so on.

!!! info "If you are as lazy as we are ..."
    In order to automate this process, check [SmartCD Feature](smartcd.md). It will run those commands when entering 
    and leaving the project directory containing the `ddb.yml` file.

Docker binary shims
--- 

If you are using [Jsonnet templates](jsonnet.md) with `ddb.Binary()` function, this means that you want to have 
simple access to command execution inside docker containers. 

As the generation of the shims depends on your specific shell (cmd.exe, bash, ...), it is handled by the shell feature.

Each declared binary inside `.jsonnet` file generates a shim inside the `.bin` project directory 
(directory configured in `shell.path.directories[0]`), and available in your shell after running `$(ddb activate)`.

!!! example "Access to PostgreSQL commands the native way"
    If you have a PostgreSQL container, you may need to run commands like ...
      - `psql` - PostgreSQL client binary.
      - `pg_dump` - PostgreSQL command line tool to export data to a file.
   
    Instead of writing a long and impossible to remember docker commmand, you should declare them using `ddb.Binary()` 
    function in `docker-compose.yml.jsonnet` file.
    
    ```json
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
    
    Then, run `ddb configure`, which will generate executable shim file in the `.bin` folder.
    
    Finaly, run `$(ddb activate)` to update your `PATH` and bring those commands to your local environment.

    Now, `psql` and `pg_dump` are available as if they were native commands.

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

!!! example "Make a composer dependency available globally"
    When you are working on PHP/Composer project, some commands are available inside `vendor` path.
    
    For drupal developers, [Drush](https://www.drush.org/) commands is available through `vendor/drush/drush/drush` 
    binary.
    
    Instead of writing the full path of this binary each time, you can declare an alias in ddb configuration. 
    
    ```yaml
    shell:
      aliases:
        drush: vendor/drush/drush/drush
    ```
    
    A binary shim will be created and added to the `PATH` thanks to ddb so you will able to use it from you project 
    root folder: 
    
    ```shell
    drush cr
    ```  