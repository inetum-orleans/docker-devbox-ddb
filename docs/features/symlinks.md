Symlinks
===

This feature is a way to automatically create symlinks in your project.

One of the common use we have is project with configurations for each environment (dev, stage, prod).
With `symlinks` feature, depending on environment, the final file is link to the one from environment. 

!!! summary "Feature configuration (prefixed with `symlinks.`)"
    === "Simple"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `disabled` | boolean<br>`false` | Should this feature be disabled ? |
        | `suffixes` | string[]<br>`['.${core.env.current}']` | A list of filename suffix to include. |
        | `excludes` | string[]<br>`[]` | A list of glob of filepath to exclude. |

    === "Advanced"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `includes` | string[]<br>`['*.${core.env.current}{.*,}']` | A list of glob of filepath to include. It is automatically generated from `suffixes`. |
    
Symlink creation
---
Bound to events `file:found`, `file:deleted` and `file:generated`, each file retrieved will
be compared to lists of configurations `includes` and `excludes` to check it is handled or not.

If it is a match, symlink will be generated, or deleted if it is a `events.file.deleted` event.

!!! example "Create `.env` symlink from `.env.prod`"
    In many frameworks, we want to have different `.env` files depending on `core.env.current` value. 
    
    Let's say we have created a `.env.prod` which contains production environment configuration.
    Instead of manually copying the file or creating a symlink, this will create `.env` symlink pointing to `.env.prod` 
    file if `core.env.current` is set to `prod`.

!!! tip
    It can also be chained with any other ddb template generation, such as [jinja](./jinja.md) and [ytt](./ytt.md)
