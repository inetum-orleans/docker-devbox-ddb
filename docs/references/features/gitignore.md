Gitignore
===

The Gitignore feature provides automation to the management of .gitignore files of the project.

Feature Configuration
---

- `disabled`: Definition of the status of the feature. If set to True, all gitignore automations will be disabled.
    - type: boolean
    - default: False
 
??? example "Configuration example"
    ```yaml
    gitignore:
      disabled: false
    ```
Automatic management of gitignore
---

When you are working on ddb project, there is a lot of files generated: the parsed templates files, the binary shims, ...

As those files may depends on your environment, they must not be added to the git repository and must be added to 
the list of git ignored files.

Because adding them manually is tedious, if this feature is enable, when ddb generates those files, they are 
automatically added to the nearest `.gitignore` file.