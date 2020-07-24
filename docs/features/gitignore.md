Gitignore
===

The Gitignore feature provides automation to the management of .gitignore files of the project.

Feature Configuration
---

- `disabled`: Definition of the status of the feature. If set to True, all gitignore automations will be disabled.
    - type: boolean
    - default: False
 
!!! example "Configuration"
    ```yaml
    gitignore:
      disabled: false
    ```
Automatic management of gitignore
---

ddb generates a bunch of files inside your project sources: target files from templates, binary shims, ...

As those files may depends on your environment configuration, they should not be added to the git repository and must 
be added to `.gitignore`, for them to be generated on each environment without spoiling git repository.

Because adding them manually to `.gitignore` is a chore, ddb automatically adds all generated files to the nearest 
`.gitignore` file, from top to bottom of filesystem folder hierarchy. The other way round, if a generated file source 
is removed, the target file will also be removed from `.gitignore` file.
