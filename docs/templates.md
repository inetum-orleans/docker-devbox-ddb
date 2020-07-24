Templates
===

**ddb** provides some template engine support, like [Jinja](https://jinja.palletsprojects.com/), 
[Jsonnet](https://jsonnet.org/) and [Ytt](https://get-ytt.io/).

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

Jsonnet
---

Jsonnet mostly works like others template engines, but it is kind of special, because the extension of the target file 
format is used to guess the final output of the file so it can output YAML or JSON either.

- `docker-compose.yml.jsonnet` is processed by [jsonnet](features/jsonnet.md) and produces a yaml as output.

- `data.jsonnet.json` is processed by [jsonnet](features/jsonnet.md) and produces json as output.

!!! info "Jsonnet produces `json` as default output"
    By default, [jsonnet](features/jsonnet.md) produces json as output, unless extension of the target file is `.yml`.

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

- `settings.yaml.prod` -> *Settings for prod environment*
- `settings.yaml.stage` -> *Settings for stage environment*
- `settings.yaml.dev` -> *Settings for dev environment*
- `settings.yaml` -> *Symlink pointing to file based on `core.env.current`*

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