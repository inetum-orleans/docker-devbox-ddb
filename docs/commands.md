Commands
========

If you run **ddb** with no argument, the usage is displayed.

!!! info "ddb usage"
    ```
    usage: ddb [-h] [-v] [-vv] [-s] [-x] [-c] [-w] [-ff] [--version]
               {run,init,configure,features,config,activate,deactivate} ...
    
    positional arguments:
      {run,init,configure,features,config,activate,deactivate}
                            Available commands
        run                 Display command to run project binary
        init                Initialize the environment
        configure           Configure the environment
        features            List enabled features
        config              Display effective configuration
        activate            Write a shell script to be executed to activate
                            environment
        deactivate          Write a shell script to be executed to deactivate
                            environment
    
    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbose         Enable more logs
      -vv, --very-verbose   Enable even more logs
      -s, --silent          Disable all logs
      -x, --exceptions      Display exceptions on errors
      -c, --clear-cache     Clear all caches
      -w, --watch           Enable watch mode (hot reload of generated files)
      -ff, --fail-fast      Stop on first error
      --version             Display the ddb version and check for new ones.
    ```

Positional argument match **command** names: `run`, `init`, `configure`, `features`, `config`, `activate`, `deactivate`.

Some **optional arguments are available globally**, regardless the command. These are placed **before the command name**.

Some **commands support additional arguments** that can be listed with `--help` flag after the command name. 
Those are placed **after the command name**.

!!! info "`ddb config` additional arguments"
    `ddb config --help`

        ddb config --help
           usage: ddb config [-h] [--variables]
           
           optional arguments:
             -h, --help   show this help message and exit
             --variables  Output as a flat list of variables available in template
                          engines

!!! info "Watch mode"
    When setting up a project, you have to execute `ddb configure` many times while trying to configure the project 
    environment.
    
    ddb provides a `--watch` flag to enable Watch mode.
    
    - `ddb --watch configure`
    - `ddb -w configure`
    
    The command will run forever and listen for system file events to perform actions.

Available commands
---

- **ddb-init**

TODO

- **ddb features**

This action allows you to check the list of enabled features with a short explanation of what they do. 

- **ddb config**

Display the effective configuration after merge of all configuration files from possible locations.

Read more: [Configuration](configuration.md)
    
!!! tip "Tip: Use --variables to check what is available in template engines"
    
    ddb effective configuration is used as context inside all template engine processing (Jinja, jsonnet, ytt, ...)
    
    When working with templates, you might want to include some configuration values into the template.
    
    You can use `--variables` option to display the whole configuration as a flat and dotted notation, as it can be 
    tedious to retrieve the full variable name from the default `yaml` output. 

- **ddb configure**

TODO

- **ddb activate**

Display a script for the configured shell that must be evaluated to active the project environment inside the current 
shell session.

Read more: [Shell feature](features/shell.md)

- **ddb deactivate**

Display a script for the configured shell that must be evaluated to deactivate the project environment inside the current 
shell session.

Read more: [Shell feature](features/shell.md)

- **ddb run**

Display the command line to evaluate in the configured shell to run the registered binary.
