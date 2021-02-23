Gitignore
===

The Gitignore feature provides automation to the management of .gitignore files of the project.

!!! summary "Feature configuration (prefixed with `gitignore.`)"
    | Property | Type | Description |
    | :---------: | :----: | :----------- |
    | `disabled` | boolean<br>`false` | Should this feature be disabled ? |
    | `enforce` | string[]<br>`['*ddb.local.*']` | List of file globs to force into `.gitignore`. |

Automatic management of gitignore
---

ddb generates a bunch of files inside your project sources: target files from templates, binary shims, ...

As those files may depends on your environment configuration, they should not be added to the git repository and must 
be added to `.gitignore`, for them to be generated on each environment without spoiling git repository.

Because adding them manually to `.gitignore` is a chore, ddb automatically adds all generated files to the nearest 
`.gitignore` file, from top to bottom of filesystem folder hierarchy. The other way round, if a generated file source 
is removed, the target file will also be removed from `.gitignore` file.

Finally, using the `enforce` configuration, you can force files to be added to the gitignore, even if it is not a file 
managed by ddb.