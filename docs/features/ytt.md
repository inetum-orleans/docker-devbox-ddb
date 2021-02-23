ytt
===

[YTT](https://carvel.dev/ytt/) is a template engine dedicated to yaml.

!!! summary "Feature configuration (prefixed with `ytt.`)"
    === "Simple"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `disabled` | boolean<br>`false` | Should this feature be disabled ? |
        | `suffixes` | string[]<br>`['.ytt']` | A list of filename suffix to include. |
        | `extensions` | string[]<br>`['yaml', 'yml', '']` | A list of glob of supported extension. |
        | `excludes` | string[]<br>`[]` | A list of glob of filepath to exclude. |
        | `args` | string[]<br>`[]` | A list of arguments to pass to ytt. |
        | `depends_suffixes` | string[]<br>`['.data', '.overlay']` | File suffix to use for ytt dependency files. |

    === "Advanced"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `includes` | string[]<br>`['*.ytt{.yaml,.yml,}']` | A list of glob of filepath to include. It is automatically generated from `suffixes` and `extensions`. |
        | `keywords` | string[]<br> |  |
        | `keywords_escape_format` | string[]<br>`%s_` |  |
