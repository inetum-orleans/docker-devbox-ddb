Configuration
=============

**ddb** use **yaml configuration files**:

- `ddb.yml`, the main configuration file
- `ddb.<env>.yml`, the environment configuration file override, where `<env>` can be `dev`, `stage`, `ci` or `prod`.
- `ddb.local.yml`, the configuration file local override.

Those files can be placed in those **directories**:

- Inside `~/.docker-devbox/ddb`
- Inside `~/.docker-devbox`
- Inside the project directory root

If many configuration files are found, they are **merged** with given filenames and directories order.

This configuration is **used internally** by feature actions, but is also injected as **context for each supported 
template engine**. You can add your own project properties inside the configuration file so they are available inside 
template engines.

!!! question "How to check effective configuration"
    You can run `ddb config` to view the effective configuration. Use `--full` option to display the whole 
    configuration including default and internal values, and `--file` to split the configuration settings by 
    configuration files.
    
Each feature holds it's **own configuration** section under the **name of the feature**. For details about supported 
configuration settings, please check the documentation of related feature.

!!! info "Default merge behavior"

    By default, when ddb merge a configuration file, objects are be deeply merged, but any other data type is overriden.
    
    *ddb.yml*
    
    ```yaml
    jsonnet:
      docker:
        compose:
          excluded_services: ['python']
    ```
    
    *ddb.local.yml*
    ```yaml
    jsonnet:
      docker:
        compose:
          excluded_services: []
    ```
    
    *effective configuration (ddb config)*
    ```yaml
    jsonnet:
      docker:
        compose:
          excluded_services: []
    ```
    
    As you can see lists are overriden by default too.
    
!!! info "Custom merge behavior"

    You can specify custom merge behavior using an object containing two properties

    - `value`: The actual value to merge
    - `merge`: The merge strategy to apply 

    For lists, you may use the following merge strategies:
    
    - `override` *(default)*
    - `append`
    - `prepend`
    - `insert`
    - `append_if_missing`
    - `prepend_if_missing`
    - `insert_if_missing`
    
    For objects, you may use the following merge strategies:
    
    - `merge` *(default)*
    - `override`
    
    *ddb.yml*
    
    ```yaml
    jsonnet:
      docker:
        compose:
          excluded_services: ['python']
    ```
    
    *ddb.local.yml*
    ```yaml
    jsonnet:
      docker:
        compose:
          excluded_services:
            merge: append_if_missing
            value: ['gunicorn']
    ```
    
    *effective configuration (ddb config)*
    ```yaml
    jsonnet:
      docker:
        compose:
          excluded_services: ['python', 'gunicorn']
    ```

!!! info "Configuration and environment variables"
    To override any configuration setting, you may set an environment variable. 
    
    To convert the property name from dotted notation to environment variable, you should write in UPPERCASE, add 
    `DDB_` prefix replace `.` with `_`. For instance, `core.domain.ext` can be overriden with `DDB_CORE_DOMAIN_EXT` 
    environment variable.
    
    Variables lists can be referenced with `[0]`, `[1]`, ..., `[n]`
    
    When activating the environment `$(ddb activate)` with [shell feature (Environment activation)](#environment-activation), 
    the whole configuration is also exported as environment variables using the same naming convention.

!!! info "Extra configuration files"
    You may add additional configuration files using core.configuration.extra_files configuration property into default 
    configuration files.

    ```yml
    core:
      configuration:
        extra: ['ddb.custom.yml']
    ```

    This will load `ddb.custom.yml` configuration file from each supported configuration directories. `ddb.local.yml` 
    still has the priority other those extra configuration files.
