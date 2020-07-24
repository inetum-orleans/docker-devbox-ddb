Templates
===

**ddb** provides some template engine support, like [Jinja](https://jinja.palletsprojects.com/), 
[Jsonnet](https://jsonnet.org/) and [ytt](https://get-ytt.io/).

Each template engine is implemented in it's own feature, [jinja](features/jinja.md), 
[jsonnet](features/jsonnet.md) and [ytt](features/ytt.md).

!!! info "Files are automatically processed"
    Files are automatically processed by a template engine based on file extension.
    
    `Dockerfile.jinja` is processed by [jinja](./features/jinja.md) and produces `Dockerfile` file.
    
    The template filename extension can also be found when placed just before the target filename extension.
    
    Both `data.json.jinja` and `data.jinja.json` is processed by [jinja](./features/jinja.md) and produces `data.json`.

!!! tip "Automate your deployments for all environments"
    
    Templates are perfect for configuration files that should change for each environment, or to embed some global 
    configuration settings into many static configuration files.
    
    You should abuse of templates to make deployment on various environment a breeze, as the application will 
    auto-configure based on ddb configuration of each environment.
    
    `git clone`, `ddb configure` and that's all ! Your application is ready to run on dev, stage or production 
    environment.
    
     Keep in mind that you can freely add any setting inside `ddb.yml` [project configuration](./configuration.md), it 
     so you can retrieve them from any template.
     
Jinja
---

[Jinja](https://jinja.palletsprojects.com/) is a modern and designer-friendly templating language, modelled after Django’s templates. It's a general purpose 
templating engine that doesn't target any particular file format.

!!! tip "Write `Dockerfile.jinja` instead of raw `Dockerfile`"
    Jinja is really handy to make your Dockerfile dynamic.
    
    Writing `Dockerfile.jinja` files instead of raw `Dockerfile` is recommended in ddb, and mandatory when using [fixuid 
    feature](features/fixuid.md).

Jsonnet
---

[Jsonnet](https://jsonnet.org/) is a data templating language for app and tool developers. It's an extension of json 
and can only output `JSON`.

In ddb, Jsonnet mostly works like others template engines, but the extension of the target file is used to guess the 
target output format: `JSON` or `YAML`. As Jsonnet can only output `JSON`, `YAML` output is converted from `JSON` 
thanks to python environment.

- `docker-compose.yml.jsonnet` is processed by [jsonnet](features/jsonnet.md) and produces a yaml as output.

- `data.jsonnet.json` is processed by [jsonnet](features/jsonnet.md) and produces json as output.

!!! info "Jsonnet produces `json` as default output"
    By default, [jsonnet](features/jsonnet.md) produces json as output, unless extension of the target file is `.yml`.

!!! tip "Write `docker-compose.yml.jsonnet` instead of raw `docker-compose.yml`"
    **ddb** brings many docker and docker-compose features through jsonnet, so you'd better writing a 
    `docker-compose.yml.jsonnet` file instead of a raw `docker-compose.yml` configuration.
    
    Read more: [jsonnet Feature (Docker-compose jsonnet library)](features/jsonnet.md#docker-compose-jsonnet-library)

ytt
---

[ytt](https://get-ytt.io/) is a templating tool that understands YAML structure allowing you to focus on your data 
instead of how to properly escape it.

Ytt templates are a superset of YAML and can only generate yaml files.

!!! tip "You may like [ytt](https://get-ytt.io/), but you'd better focus on learning [Jsonnet](https://jsonnet.org/)"
    Because [Jsonnet](https://jsonnet.org/) supports custom functions, and both `JSON` et `YAML` output, we consider 
    [ytt](https://get-ytt.io/) as a secondary template engine. 
    
    It's available and fully supported in ddb, so you can use it to template any `YAML` configuration files inside your application.
    
    But if you implement `docker-compose.yml.ytt`, you won't be able to use all features available in ddb docker-compose jsonnet library.
    
    Read more: [jsonnet Feature (Docker-compose jsonnet library)](features/jsonnet.md#docker-compose-jsonnet-library)
    
    
Symlinks
---

[Symlinks feature](features/symlinks.md) allow to create a symlink from many possible files, each source file matching 
a supported environment.

Even if it's not based on a template engine, [symlinks feature](features/symlinks.md) shares some of behavior from 
other template based features as it generates a symlink from another file.

By default, ddb holds the following configuration settings:

```yaml
core.env.available: ['prod', 'stage', 'ci', 'dev']
core.env.current: dev
```

- `core.env.available` contains all supported environment values
- `core.env.current` match the actual environment.

Consider a project with a configuration file named `settings.yaml`. This file should be different for each environment.
 
Thanks to ddb and without implementing custom configuration logic inside the application, you can create a file for each environment, and the symlink matching the current environment is generated.

- *`settings.yaml.prod`* -> *Settings for prod environment*
- *`settings.yaml.stage`* -> *Settings for stage environment*
- *`settings.yaml.dev`* -> *Settings for dev environment*
- **`settings.yaml`** -> *Symlink pointing to file based on `core.env.current`*

If `core.env.current` is set to `dev`, `settings.yaml` symlink points to `settings.yaml.dev`

If `core.env.current` is set to `stage`, `settings.yaml` symlink points to `settings.yaml.stage`

If `core.env.current` is set to `prod`, `settings.yaml` symlink points to `settings.yaml.prod`

!!! question "What if no file exists for the current environment ?"
    There's no `settings.yaml.ci` file, but if `core.env.current` is set to `ci`, `settings.yaml` symlink will still point 
    to `settings.yaml.dev`
    
    The fallback behavoir is to find the first existing file on the right of `ci` in `core.env.available`.
    
    If `settings.yaml.dev` doesn't exists, no symlink is created at all.

So now, you can refer to this symlink to load the configuration inside your application, so it will switch 
automatically when deploying on `stage` or `prod` environment.

!!! question "Where to use a symlink, where to use a template ?"
    Use a **symlink** where changes are conditionned by `core.env.current` environment setting and affects most of the 
    configuration file content. 
    
    Use a **template** where changes are conditionned by any other environnement setting, or when changes affects a very 
    small portion of the configuration file content.
    
    Anyway, **You can use both symlink and template** to generate a single configuration file as ddb is reactive and 
    supports natural action chaining. 
    
    - You can create a symlink first, and then resolve a template.
    
        - *`settings.yaml.ytt.prod`* -> *Settings template for prod environment*
        - *`settings.yaml.ytt.stage`* -> *Settings template for stage environment*
        - *`settings.yaml.ytt.dev`* -> *Settings template for dev environment*
        - *`settings.yaml.ytt`* -> *Symlink pointing to settings template file based on `core.env.current`*
        - **`settings.yaml`** -> *Generated settings file from Symlink through ytt template engine*
    
    - Or you can resolve a template first, and then create a symlink.
    
        - *`settings.yaml.prod.ytt`* -> *Settings template for prod environment*
        - *`settings.yaml.stage.ytt`* -> *Settings template for stage environment*
        - *`settings.yaml.dev.ytt`* -> *Settings template for dev environment*
        - *`settings.yaml.prod`* -> *Generated settings file for prod environment*
        - *`settings.yaml.stage`* -> *Generated settings file for stage environment*
        - *`settings.yaml.dev`* -> *Generated settings file for dev environment*
        - **`settings.yaml`** -> *Symlink pointing to generated settings file based on `core.env.current`*