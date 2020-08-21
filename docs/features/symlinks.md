Symlinks
===

This feature is a way to automatically create symlinks in your project.

One of the common use we have is project with configurations for each environment (dev, stage, prod).
With the `symlinks` feature, depending on the environment, the final file is link to the one from the environment. 

Feature Configuration
---
- `disabled`: Definition of the status of the feature. If set to True, this feature will not be triggered.
    - type: boolean
    - default: False
- `excluded`: The list of file to exclude from the symlink creation.
    - type: array of string
    - default: []
- `includes`: The source file format to search for. If not override, it is generated using the `suffixes` list.
    - type: array of string
    - default: ['*.<suffixes>{.*,}']
- `suffixes`: The list of suffixes to generate symlink for. If not override, it is generated using the `core.env.current`
    configuration.
    - type: array of string
    - default: ['.<core.env.current>']

!!! example "Configuration."
    ```yaml
    symlinks:
      disabled: false
      includes:
      - '*.dev{.*,}'
      suffixes:
      - .dev
    ```
    
Symlink creation
---
Bounded to the events `events.file.found`, `events.file.deleted` and `events.file.generated`, each file retrieved will
be compared to lists of configurations `includes` and `excludes` to check it is handled or not.

If it is a match, the symlink will be generated, or deleted if it is a `events.file.deleted` event.

!!! note 
    It can also be chained with any other ddb template generation, such as [jinja](./jinja.md) and [ytt](./ytt.md)

!!! example
    In Symfony, we want to have different `.env` files depending on the `core.env.current` variable. 
    
    Let's say we have created a `.env.prod` which contains production environment configuration. 
    Instead of manually copying the file, or created a symlink, if the `core.env.current` is set to **prod**, the 
    `symlinks` feature will create the `.env` symlink pointing to the `.env.prod` file.