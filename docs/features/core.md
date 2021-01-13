Core
===

Core feature contains some key configuration like domain name and current active environement. Those configuration 
settings may impact many other features indirectly.

It also handle the two following basic commands : `ddb features` and `ddb config`. Check [command](../commands.md) page for details about those commands.


!!! summary "Feature configuration (prefixed with `core.`)"
    === "Simple"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `disabled` | boolean<br>`false` | Should this feature be disabled ? |
        | `domain.sub` | string<br>`${project.name}` | The domain to use for the domain generation. This is the constant part of the domain, that should not vary between environment. |
        | `domain.ext` | string<br>`test` | The extension to use for the domain. This is the last part, of your domain name, that may vary between environment. |
        | `env.current` | string<br>`${env.available}[-1]` | Current active environment. Default value is `dev`, or the last value of `env.available`. |
        | `project.name` | string<br>`<Directory name of ${path.project_home}>` | The project name. This is used by many templates and to generate other default values like `domain.sub`.
    === "Advanced"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `env.available` | string[]<br>`['prod', 'stage', 'ci', 'dev']` | List of available environments. You should any new custom environment to support here before trying to set `env.current` to this custom environment.|
        | `required_version` | string | Minimal required `ddb` version for the project to work properly. If `required_version` is greater than the currently running one, ddb will refuse to run until it's updated. |
        | `path.ddb_home` | string<br>`${env:HOME}/.docker-devbox/ddb` | The path where ddb is installed. |
        | `path.home` | string<br>`${env:HOME}/.docker-devbox` | The path where docker devbox is installed. |
        | `path.project_home` | string | The project directory. |
        | `process` | **Process**[] | List of process configurations. A process configuration allow to add custom arguments before and after a command executed internally (like `git`). |
    === "Internal"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `os` | string<br>`posix` | The current operating system. |
        | `github_repository` | string<br>`gfi-centre-ouest/docker-devbox-ddb` | List of process configurations. A process configuration allow to add flags before and after a command normaly runned by ddb (like `git`). |

!!! summary "Process configuration (used in `core.process`)"

    | Property | Type | Description |
    | :---------: | :----: | :----------- |
    | `bin` | string<span style="color:red">*</span> | The process path to override. |
    | `prepend` | string\|string[]<br> | Arguments to prepend to default arguments. |
    | `append` | string\|string[] | Arguments to append to default arguments. |

!!! quote "Defaults"
    ```yaml
    core:
      disabled: false
      domain:
        ext: test
        sub: docker-devbox
      env:
        available:
        - prod
        - stage
        - ci
        - dev
        current: dev
      github_repository: gfi-centre-ouest/docker-devbox-ddb
      os: posix
      path:
        ddb_home: /home/devbox/.docker-devbox/ddb
        home: /home/devbox/.docker-devbox
        project_home: /home/devbox/projects/docker-devbox
      process: {}
      project:
        name: docker-devbox
      github_repository:
    ```
