Permissions
===

Permissions can be a bit tedious to update. Plus, you might want to define the right permissions on a file once and for
all.

Well, this feature is made for you!

Feature Configuration
---
- `disabled`: Definition of the status of the feature. If set to True, this feature will not be triggered.
    - type: boolean
    - default: False
- `specs`: Definition of the files with their permissions mods
    - type: Map<file:string, mod:string>
    - default: null

!!! example "Configuration"
    ```yaml
    permissions:
      disabled: false
      specs: null
    ```

Permission update
---

The permission management is bound the two following events : `file.found` and `file.generated`.

When one of those is raised, the system check if the file associated to the event is part of the `specs` configuration.
If it is part of it, the feature will update the permissions of the file accordingly to the mod defined.
Otherwise, the feature will not process the given file.