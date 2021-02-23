Version
===

Version feature extracts information about the version of your project from local git repository.

!!! summary "Feature configuration (prefixed with `version.`)"
    | Property | Type | Description |
    | :---------: | :----: | :----------- |
    | `disabled` | boolean<br>`false` | Should this feature be disabled ? |
    | `branch` | string<br>`<current git branch>` | The current branch of the project. |
    | `hash` | string<br>`<current git hash>` | The hash of the current commit. |
    | `short_hash` | string<br>`<current git short hash>` | The short version of the hash of the current commit. |
    | `tag` | string<br>`<current git tag>` | The current git tag. |
    | `version` | string<br>`<current project version>` | The current project version. |
