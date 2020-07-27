Docker
===

The docker feature is one of the most important one. From processing docker-compose configuration to 
handling simple execution of commands into docker containers, it contains a lot of functionalities.

docker-compose configuration processing
---

When a `docker-compose.yml` is found or generated from templates, the content is parsed.

All labels prefixed `ddb.emit.` are processed and converted into event and event arguments.

!!! info "Creation of binaries"
    Whether you use `ddb.Binary()` in jsonnet template or manually add labels to your `docker-compose.yml`, they 
    are converted into ddb configuration and shims are generated as simple executable commands by the [shell](shell.md)
    features, thanks to `docker:binary` event.
    
Feature configuration
---
As docker is at the heart of ddb, it has one of the largest collection of parameters. 

- `disabled`: Definition of the status of the feature. If set to True, docker feature will not be triggered.
    - type: boolean
    - default: False
- `build_image_tag_from_version`: Define if an automatic tag must be added to image name in docker-compose file.
    - type: boolean
    - default: True
- `build_image_tag`: The tag added to the image name in docker-compose file.
    - type: string
    - default: <retrieved from git branch or tag name>
- `cache_from_image`: 
    Mainly used for build purpose in CI, it enable the cache_from settings for services in docker-compose.yml generation.
    - type: boolean
    - default: False
- `compose.project_name`: The name given to the project. 
    - type: string
    - default: retrieved from project folder name
- `compose.network_name`: The name of the default docker network for this project. 
    - type: string
    - default: retrieved from compose.project.name, suffixed with _default
- `debug.disabled`: Enable or disable debug functionalities integrated in docker-compose.yml.jsonnet automation.
    - type: boolean
    - default: False
- `debug.host`: The address to contact for debug functionalities.
    - type: string
- `directory`: The directory where container Dockerfile are stored.
    - type: string
    - default: value : .docker
- `interface`: TODO explain what it is used for.
    - type: string
    - default: value : docker0
- `ip`: TODO explain what it is used for.
    - type: string
    - default: value : 172.17.0.1
- `path_mapping`: TODO explain what it is used for.
    - type: object
    - default: value : {}
- `port_prefix`: The prefix to add to default ports for exposition to host.
    - type: integer
    - default: value : 373
- `registry.name`: The address of the docker image registry.
    - type: string|null
- `registry.repository`: The repository for this project docker images.
    - type: string|null
- `restart_policy`: The strategy to use for docker restart on crash or host start event
    - type: string
    - default: depending on the environment : on dev it is set to 'no', on other it is set to 'yes'
- `reverse_proxy.certresolver`: TODO explain what it is used for.
    - type: string|null
- `reverse_proxy.network_id`: TODO explain what it is used for.
    - type: string|null
    - default: reverse-proxy # TODO
- `reverse_proxy.network_names`: TODO explain what it is used for.
    - type: object
    - default: {reverse-proxy: reverse-proxy} # TODO
- `reverse_proxy.redirect_to_https`: Set if all traffic must be redirected to https.
    - type: boolean|null
    - default: null
- `reverse_proxy.type`: Define the type of reverse_proxy for configuration management
    - type: string
    - default: null # TODO
- `user.uid`: The UID to use inside a container
    - type: number
    - default: Automatically retrieve the UID of the current user
- `user.gid`: The GID to use inside a container
    - type: number
    - default: Automatically retrieve the GID of the current user
    
!!! example "Configuration"
    ```yaml
    docker:
      build_image_tag: master
      build_image_tag_from_version: true
      cache_from_image: false
      compose:
        network_name: project_default
        project_name: project
      debug:
        disabled: false
        host: 192.168.85.1
      directory: .docker
      disabled: false
      interface: docker0
      ip: 172.17.0.1
      path_mapping: {}
      port_prefix: 373
      restart_policy: 'no'
      reverse_proxy:
        certresolver: null
        network_id: reverse-proxy
        network_names:
          reverse-proxy: reverse-proxy
        redirect_to_https: null
        type: traefik
      user:
        gid: 1000
        uid: 1000
    ```