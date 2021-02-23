Cookiecutter
===

Download and generate files from [Cookiecutter](https://github.com/cookiecutter/cookiecutter) templates.

This can be used for [djp packages](../djp.md) or any other Cookiecutter with 
[download command](../commands.md#ddb-download).

!!! summary "Feature configuration (prefixed with `cookiecutter.`)"
    === "Simple"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `disabled` | boolean<br>`false` | Should this feature be disabled ? |
        | `templates` | **Template**[] | List of templates to download |
    === "Advanced"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `default_context` | Dict[str, Any] | List of available environments. You should any new custom environment to support here before trying to set `env.current` to this custom environment.|
    === "Internal"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `cookiecutters_dir` | string | Temporary directory for download templates |
        | `replay_dir` | string | Temporary directory to store replay |

!!! summary "Template configuration (used in `cookiecutter.templates`)"
    === "Simple"    
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `template` | string<span style="color:red">*</span> | Template to download |
        | `output_dir` | string | Output directory relative to project root. If not defined, it will use `directory` value defined in template's `cookiecutter.json` |
        | `checkout` | string | tag/branch to use for the template |
        | `extra_context` | dict[str, Any] | Extra context to use to render cookiecutter template. This can be used to customize values from template's `cookiecutter.json` |
    === "Advanced"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `password` | dict[str, Any] | Password to use for authentication |
        | `no_input` | boolean<br>`true` | Set to `false` to make cookiecutter ask questions. |
        | `replay` | boolean<br>`false` |  |
        | `overwrite_if_exists` | boolean<br>`true` |  |
        | `config_file` | string |  |
        | `default_config` | dict[str, Any] |  |

!!! tip "Generate `.patch` files to track your changes"
    
    If you need to apply some modification on downloaded content, you should generate `.patch` files (unified diff) 
    of the output directory of the template.

    Any `.patch` file available in the output directory will be automatically applied when invoking `ddb download` 
    command later, so you changes are kept while downloading a new version of the template.
