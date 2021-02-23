Git
===

The Git feature provides automation relatives to the git configuration of the project.


!!! summary "Feature configuration (prefixed with `git.`)"
    | Property | Type | Description |
    | :---------: | :----: | :----------- |
    | `disabled` | boolean<br>`false` | Should this feature be disabled ? |
    | `fix_files_permissions` | boolean<br>`true` | Should file permissions be fixed from git index (executable flags) ? |

!!! example "Configuration"
    ```yaml
    git:
      disabled: false
      fix_files_permissions: true
    ``` 
Fix files permissions
---

When you clone or update a repository, it may contain executable files. If you are working on windows and using some 
synchronisation too to synchronize those files, executable flags may be lost.

With Git, you can store the executable flag into the repository. To do so, you can execute the following command : 

```
git update-index --chmod=+x <your_file>
```

But this will not update the flag on the system automatically.

Unless `git.fix_files_permissions` is set to `false` in ddb configuration, files marked as executable in git repository
have their permissions fixed on `ddb configure` command. 