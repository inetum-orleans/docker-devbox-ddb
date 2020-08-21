Copy
===

The `copy` feature is a simple way to automatically copy files from one folder to another. 

This feature is bounded to the [`init` command](../commands.md).

Feature configuration
---

Base configuration : 

- `disabled`: Definition of the status of the feature. If set to True, this feature will not be triggered.
    - type: boolean
    - default: False
- `specs`: The list of files/pattern to files to copy
    - type: list of Spec configuration
    - default: []

Spec configuration :

- `source`: The source file to copy. it can be a local file, or an internet one.
    - type: string
    - required: true
- `destination`: The destination folder.
    - type: string
    - default: `.`
- `filename`: The destination filename. If not set, it will use the same name as the original file name.
    - type: string
    - required: false
- `dispatch`: The root folders to copy to. If not set, it will use the full path of `destination` configuration relative
            to the project root folder.
    - type: List of string
    - required: false
    
!!! example "Configuration"
    ```yaml
    copy:
      disabled: false
    ```
    
!!! example "Configuration with specs"
    ```yaml
    copy:
      disabled: false
      specs: 
        - source: 'https://github.com/boxboat/fixuid/releases/download/v0.4/fixuid-0.4-linux-amd64.tar.gz'
          destination: '.docker'
          filename: 'fixuid.tar.gz'
    ```
    When running `ddb init` with this configuration, it will download the file from the source and copy it into
    `<project_root>/.docker/fixuid.tar.gz`