Configuration
=============

**ddb** use **yaml configuration files**:

- `ddb.yml`, the main configuration file
- `ddb.local.yml`, the configuration file override.

Those files can be placed in those **directories**:

- Inside `~/.docker-devbox/ddb`
- Inside `~/.docker-devbox`
- Inside the project directory root

If many configuration files are found, they are **merged** with given filenames and directories order.

This configuration is **used internally** by feature actions, but is also injected as **context for each supported 
template engine**. You can add any data structure inside the configuration file so this data is available inside 
template engines.

!!! question "How to check effective configuration"
    You can run `ddb config` to view the merged effective configuration.
    
Each feature holds it's own configuration section under the name of the feature. For details about each supported 
configuration setting, please check the documentation of each feature.