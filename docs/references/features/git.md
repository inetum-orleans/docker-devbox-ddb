Git
===

The Git feature provides automation relatives to the git configuration of the project.

Feature Configuration
---

- `disabled`: Definition of the status of the feature. If set to True, all git automations will be disabled.
    - type: boolean
    - default value: False
              
- `fix_files_permissions`: Activate the file access in regard to git index 
    - type: boolean
    - default value: true

??? example "Configuration example"
    ```yaml
    git:
      disabled: false
      fix_files_permissions: true
    ``` 
Fix Files Permissions automation
---

When you clone or update a repository, it may contains executable files such as php binaries. By default, they does not 
have the execution flag on Linux/Unix environments. 

With Git, you can store the execution flag into the repository. To do so, you can execute the following command : 

```
git update-index --chmod=<+|->x <your_file>
```

But this will not update the flag on the system automatically.

So, if `git.fix_files_permissions` is set to true in ddb configuration, those files having an entry for the execution 
flag in Git will be updated accordingly when you execute the `ddb configure` command. 