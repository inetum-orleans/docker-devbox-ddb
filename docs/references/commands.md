Commands
---

**ddb** provide a short list of commands which are used in all project configuration and executions steps.

The ddb command
---

`ddb` command is the entrypoint for all ddb available actions. 

If you provide it with not parameters, you will be answered with the list of actions that you can execute, and a 
short explanation of what it is used for.

!!! example "Example output without argument"
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
      --version             Display the ddb version.
    ```

As you can see, only 7 actions are available at the moment. 
They all have their own set of parameters required or optional, but all of them have the `--help` flag available to let
you if they have optionals parameters.

`ddb` also add some global optional arguments which can be used in combination with actions.

!!! example "One of the most used combination : ddb -w configure"
    When setting up a project, you will have to execute quite a lot of time `ddb configure` in order to achieve the 
    right environment setup.
    
    Adding the watch flag, the configure action will make it automaticaly rerun as you update ddb managed files such as 
    templates.
    

ddb init
---

TODO : explain
    

ddb features
---

This action allows you to check the list of enabled features with a short explanation of what they do : 

!!! example "Example output"
    ```
    binary: Run some binary
    certs: Generate SSL certificates
    copy: Copy files from local filesystem or URL to one of many directories.
    core: Default commands and configuration support
    file: Find files matching given pattern
    git: Update gitignore files when a file is generated.
    gitignore: Update gitignore files when a file is generated.
    permissions: Update gitignore files when a file is generated.
    shell: Shell integration
    smartcd: Generate smartcd .bash_enter/.bash_leave files to automatically activate/deactive.
    version: Update gitignore files when a file is generated.
    docker: Docker/Docker Compose integration
    jinja: Render template files with Jinja template engine.
    jsonnet: Render jsonnet files with Jsonnet data templating language (https://jsonnet.org).
    symlinks: Creates symlinks from file with current environment value in their extension, or before their extension.
    traefik: Traefik integration
    ytt: Render ytt files with ytt (YAML Templating Tool) (https://get-ytt.io/).
    fixuid: Add fixuid to docker-compose services
    ```

ddb config
---

When working in ddb, you might want to check the compiled version of all ddb configuration : 

- ddb default one
- global environment configuration file
- project configuration file

To do so, an action exists : `ddb config`

!!! example "Example output with help flag"
    ```
    devbox@devbox ddb ±|dev ✗|→ ddb config --help
    usage: ddb config [-h] [--variables]
    
    optional arguments:
      -h, --help   show this help message and exit
      --variables  Output as a flat list of variables available in template
                   engines
    ```

If there is no argument provided, the compiled configuration will be displayed as if it was a yaml file.

When working in templates, you might want to use those configurations. 
In `yaml` format, it might be tedious to retrieve the full variable name.

Then, an optional argument have been added in order to render the configuration in flat way in which you can copy the key
and paste it into your templates : `--variables`

ddb configure
---

TODO 

ddb activate
---

TODO 

ddb deactivate
---

TODO 

ddb run
---

TODO