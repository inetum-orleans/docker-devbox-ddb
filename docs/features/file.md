File
===

As **ddb** work on file, there is a dedicated feature which is soul purpose is to walk through files from the project
directory and trigger the right event.

Feature Configuration
---

- `disabled`: Definition of the status of the feature. If set to True, all git automations will be disabled.
    - type: boolean
    - default: False
              
- `excluded`: The list of directories or files to exclude from processing
    - type: array of string
    - default: `['**/_*', '**/.git', '**/node_modules', '**/vendor']`
    
!!! example "Configuration"
    ```yaml
    file:
      disabled: false
      excludes:
      - '**/_*'
      - '**/.git'
      - '**/node_modules'
      - '**/vendor'
    ``` 
    
File walk and event triggering
---

As previously said, the soul purpose of the feature is to walk through files from the project directory, recursively.

It does not check folders and files set in `file.excludes` configuration. 
For instance, the directory `node_modules` which contains npm installed modules on the project is not process.
By doing so, the feature is faster.

When it checks for a folder, each file not excluded is put into a `file:found` event which will be caught by other 
features such as [jsonnet](./jsonnet.md) or [docker](./jsonnet.md) feature, and store those file in ddb cache.

For next executions, using this cache, the feature will detect if a file have been deleted and raise a `file.deleted`.
This event is used by the [gitignore](./gitignore.md) feature to remove the file from the gitignore if needed.

!!! info "The watch mode"
    This feature is the one that will benefit the most from the watch mode described in the [command](../commands.md) 
    section.
    
    It will then be kept active and check if a file is created, modified, moved or even deleted.