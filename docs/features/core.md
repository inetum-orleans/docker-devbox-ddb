Core
===

In order to work properly, the core of **ddb** needs some configuration too.

It also handle the two following basic commands : `ddb features` and `ddb config.
If you want more information on those, please check [command](../commands.md) page.

Feature configuration
---

- `disabled`: Definition of the status of the feature. If set to True, the core feature will not be triggered. We highly recommend not to disable it.
    - type: boolean
    - default: False
- `domain.ext`: The extension to use for the domain generation.
    - type: string
    - default: 'test'
- `domain.sub`: The domain to use for the domain generation.
    - type: string
    - default: <the name of the project>
- `env.available`: The list of environments available.
    - type: Array<string>
    - default: ['prod', 'stage', 'ci', 'dev']
- `os`: The current operating system
    - type: string
    - default: 'posix' for linux based environment
- `path.ddb_home`: The path where ddb is installed
    - type: string
    - default: $HOME/.docker-devbox/ddb (for linux based environment)
- `path.home`: The parent folder of ddb installation
    - type: string
    - default: $HOME/.docker-devbox (for linux based environment)
- `path.project_home`: The project folder
    - type: string
    - default: $HOME/projects/docker-devbox (for linux based environment)
- `process`: TODO EXPLAIN
    - type: string
    - default: {}
- `project.name`: The name of the project
    - type: string
    - default: <the name of the project directory>

!!! example "Configuration"
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
      os: posix
      path:
        ddb_home: /home/devbox/.docker-devbox/ddb
        home: /home/devbox/.docker-devbox
        project_home: /home/devbox/projects/docker-devbox
      process: {}
      project:
        name: docker-devbox
    ```