Permissions
===

Permissions can be a bit tedious to update. Plus, you might want to define the right permissions on a file once and for
all.

Well, this feature is made for you!

!!! summary "Feature configuration (prefixed with `permissions.`)"
    | Property | Type | Description |
    | :---------: | :----: | :----------- |
    | `disabled` | boolean<br>`false` | Should this feature be disabled ? |
    | `specs` | dict[string, string] | Key of the dict is a filepath glob matching the files to change, value is a chmod-like permission modifier like `+x` or `400`. |

!!! example "Add executable permission to each file in `bin/` directory"
    ```yaml
    permissions:
      specs:
        "bin/*": "+x"
    ```

Permission update
---

The permission management is performed for `file:found` and `file:generated` events.

When one of those is raised, the system check if the file associated to the event is part of the `specs` configuration.
If it is part of it, the feature will update the permissions of the file accordingly to the chmod modifier defined.
