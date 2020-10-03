Gitignore
===

The Gitignore feature provides automation to the management of .gitignore files of the project.

Feature Configuration
---

- `disabled`: Definition of the status of the feature. If set to True, all gitignore automations will be disabled.
    - type: boolean
    - default: False on `dev` environment, True on any other environment.
- `enforce`: A list of file to force into the gitignore when running `ddb configure`
    - type: array of string
    - default: ['*ddb.local.*']
 
!!! example "Configuration"
    ```yaml
    gitignore:
      disabled: false
      enforce: 
      - '*ddb.local.*'
    ```
Automatic management of gitignore
---

ddb generates a bunch of files inside your project sources: target files from templates, binary shims, ...

As those files may depends on your environment configuration, they should not be added to the git repository and must 
be added to `.gitignore`, for them to be generated on each environment without spoiling git repository.

Because adding them manually to `.gitignore` is a chore, ddb automatically adds all generated files to the nearest 
`.gitignore` file, from top to bottom of filesystem folder hierarchy. The other way round, if a generated file source 
is removed, the target file will also be removed from `.gitignore` file.

Finaly, using the `enforce` configuration, you can force files to be added to the gitignore, even if it is not 
a file managed used by ddb.