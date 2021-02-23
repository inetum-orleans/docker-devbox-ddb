Commands
========

If you run **ddb** with no argument, the usage is displayed and showcase **available commands**.

!!! info "ddb usage"
    ```
    usage: ddb [-h] [-v] [-vv] [-s] [-x] [-c] [-w] [-ff] [--version]
               {init,configure,download,features,config,info,self-update,run,activate,deactivate,check-activated}
               ...
    
    positional arguments:
      {init,configure,download,features,config,info,self-update,run,activate,deactivate,check-activated}
                            Available commands
        init                Initialize the environment
        configure           Configure the environment
        download            Download files from remote sources
        features            List enabled features
        config              Display effective configuration
        info                Display useful information
        self-update         Update ddb to latest version
        run                 Display command to run project binary
        activate            Write a shell script to be executed to activate
                            environment
        deactivate          Write a shell script to be executed to deactivate
                            environment
        check-activated     Check if project is activated in current shell
    
    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbose         Enable more logs
      -vv, --very-verbose   Enable even more logs
      -s, --silent          Disable all logs
      -x, --exceptions      Display exceptions on errors
      -c, --clear-cache     Clear all used caches
      -w, --watch           Enable watch mode (hot reload of generated files)
      -ff, --fail-fast      Stop on first error
      --version             Display the ddb version and check for new ones.
    
    ```

Positional argument match **command** names.

Some **optional arguments are available globally**, regardless the command. These are placed **before the command name**.

Some **commands support additional arguments** that can be listed with `--help` flag after the command name. 
Those are placed **after the command name**.

**ddb configure**
---

Configure the project by scanning project files and performing actions supported by all features.

```
optional arguments:
  -h, --help  show this help message and exit
  --eject     Eject the project using the current configuration
  --autofix   Autofix supported deprecated warnings by modifying template
              sources.
```

!!! info "Watch mode"
    When setting up a project, you have to execute `ddb configure` many times while trying to configure the project 
    environment.
    
    ddb provides a `--watch` flag to enable Watch mode.
    
    - `ddb --watch configure`
    - `ddb -w configure`
    
    The command will run forever and listen for system file events to perform actions.


!!! tip "Use --eject to convert the project to a static version"

    `--eject` option can be used to convert the project to a static version and detach it from ddb. 
    Templates files are removed after generating destination files.

    It can be used to distribute sources of your project targeting current configuration only.

    You may also also set `docker.jsonnet.virtualhost_disabled` and `docker.jsonnet.binary_disabled` to `True` to remove 
    jsonnet virtualhosts and binaries from generated docker-compose.yml.

    ```bash
    DDB_OVERRIDE_JSONNET_DOCKER_VIRTUALHOST_DISABLED=1 \
    DDB_OVERRIDE_JSONNET_DOCKER_BINARY_DISABLED=1 \
    ddb configure --eject
    ```

!!! tip "Deprecated configuration properties and --autofix"

    As `ddb` evolves during time, some settings and features may become deprecated.

    When your project use some deprecated configuration property, a warning is displayed like this one.

    If you are referencing some deprecated configuration keys inside template files, like jsonnet, jinja or ytt, you
    can run `ddb configure --autofix` to automatically migrate your template sources. Keep in mind that running this 
    command will make your project future-proof, but can break things for users running older `ddb` versions.

**ddb config**
---

Display the effective configuration after merge of all configuration files from possible locations.

```
optional arguments:
  -h, --help   show this help message and exit
  --variables  Output as a flat list of variables available in template
               engines
  --full       Output full configuration
  --files      Group by loaded configuration file
```

Read more: [Configuration](configuration.md)
    
!!! tip "Use `--variables --full` options to check what is available in template engines"
    
    ddb effective configuration is used as context inside all template engine processing ([jinja](./features/jinja.md), 
    [jsonnet](./features/jsonnet.md), [ytt](./features/ytt.md), ...)
    
    When working with templates, you might want to include some configuration values into the template.
    
    You can use `--variables` and `--full` option to display the whole configuration as a flat and dotted notation, as it can be 
    tedious to retrieve the full variable name from the default `yaml` output. 

**ddb info**
---

Displays human readable informations about your project environment such as environment variables, virtual host, 
exposed ports and binaries.

```
optional arguments:
  -h, --help   show this help message and exit
  --type TYPE  Filter for a type of information between: bin, env, port and
               vhost
```

```bash 
+-----------------------------------------------+
| db                                             |
+-----------------------------------------------+
| MYSQL_DATABASE : ddb                          |
| MYSQL_PASSWORD : ddb                          |
| MYSQL_ROOT_PASSWORD : ddb                     |
| MYSQL_USER : ddb                              |
+-----------------------------------------------+
| 37306 -> 3306                                 |
+-----------------------------------------------+
| mysql                                         |
| mysqldump                                     |
+-----------------------------------------------+
```

!!! tip "Tip: Use --type to filter for a type of information"

    For instance, you want to see only virtual hosts information. 
    
    Instead of displaying every section, by writing `ddb info --type bin` you will be provided with a filtered result.
    You can choose between bin, env, port and vhost
    
    ```bash 
    +-----------------------------------------------+
    | db                                            |
    +-----------------------------------------------+
    | Binaries:                                     |
    |                                               |
    | mysql                                         |
    | mysqldump                                     |
    +-----------------------------------------------+
    ```

**ddb download**
---

Download files from remote sources like Cookiecutter templates.

!!! tip "Tip: Use djp packages to build your environment"
    
    Use published [djp packages](./djp.md) to build environment from small preconfigured docker compose services.

**ddb self-update**
---

If ddb is installed with the standalone binary and a new version is available on github, it will automatically download 
it and update the current binary.

```
optional arguments:
  -h, --help  show this help message and exit
  --force     Force update
```

**ddb features**
---

This action allows you to check the list of enabled features with a short explanation of what they do. 

```
optional arguments:
  -h, --help  show this help message and exit
```

**ddb activate**
---

Display a script for the configured shell that must be evaluated to active the project environment inside the current
shell session.

```
optional arguments:
  -h, --help  show this help message and exit
  --force     Force activation when a project is already activated.
```

!!! tip "Tip: Use $(ddb activate)"
    
    On bash, you can use `$(ddb activate)` syntax to activate the project.

Read more: [Shell feature](features/shell.md)

**ddb deactivate**
---

Display a script for the configured shell that must be evaluated to deactivate the project environment inside the
current shell session.

```
optional arguments:
  -h, --help  show this help message and exit
  --force     Force deactivation when a project is already deactivated
```

!!! tip "Tip: Use $(ddb deactivate)"
    
    On bash, you can use `$(ddb deactivate)` syntax to deactivate the project.

Read more: [Shell feature](features/shell.md)

**ddb check-activated**
---

Check if project is activated in current shell.

Read more: [Shell feature](features/shell.md)

**ddb run**
---

Display the command line to evaluate in the configured shell to run the registered binary.
