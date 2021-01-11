Docker
===

The docker feature is one of the most important one. From processing docker-compose configuration to 
handling simple execution of commands into docker containers, it contains a lot of functionalities.

docker-compose configuration processing
---

When a `docker-compose.yml` is found or generated from templates, the content is parsed.

All labels prefixed `ddb.emit.` are processed and converted into event and event arguments.

!!! summary "Feature configuration (prefixed with `symlinks.`)"
    === "Simple"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `disabled` | boolean<br>`false` | Should this feature be disabled ? |
        | `port_prefix` | integer<br>`<based on core.project.name>` | Prefix to add to default ports for exposition to host. |
        | `reverse-proxy.https` | boolean | Should services be available as HTTPS ? If unset, it is available as both HTTP and HTTPS. |
        | `reverse-proxy.redirect_to_https` | boolean | Should services redirect to HTTPS when requested on HTTP ? |
        | `reverse-proxy.certresolver` | string | certresolver to use inside reverse proxy (traefik). `letsencrypt` is supported when using `traefik` feature. |
        | `restart_policy` | string<br>`unless-stopped`/`no` | The restart policy to use for all docker-compose services. Can be `no`, `always`, `on-failure` or `unless-stopped`. Default value is `unless-stopped`, unless `core.env.current` is set to `dev` then it's set to `no`. |
        | `registry.name` | string | The name of the docker image registry (first part before `/`). |
        | `registry.repository` | string | The repository of the docker image registry (last part before `/`). |
        | `build_image_tag` | string | Define a for docker-compose services images |
        | `build_image_tag_from` | boolean\|string<br>`true` | Define if an automatic tag must be added to image name in docker-compose file. If set to a string, it should match a configuration key to use as tag source, like `version.tag`, `version.branch`, `version.version`. (see [version](./version.md) feature) |
        | `cache_from_image` | boolean<br>`false` | Mainly used for build purpose in CI, it enables docker-compose `cache_from` for services declared in `docker-compose.yml.jsonnet`. |
        | `disabled_services` | string[] | docker-compose services listed inside this property are filtered out by [jsonnet](./jsonnet.md) feature so it's not generated in `docker-compose.yml`. |
        | `debug.disabled` | boolean<br>`false` | Should debug features be generated in `docker-compose.yml` by [jsonnet](./jsonnet.md) feature ? |
        | `debug.host` | string<br>`false` | The host to connect back for debug features. |
        | `jsonnet.virtualhost_disabled` | boolean<br>`false` | Should VirtualHost generation be disabled by [jsonnet](./jsonnet.md) feature ? |
        | `jsonnet.binary_disabled` | boolean<br>`false` | Should Binary generation be disabled by [jsonnet](./jsonnet.md) feature ? |
        | `user.uid` | string | The user UID to use inside a container when [jsonnet](./jsonnet.md) `User()` function is used. |
        | `user.gid` | string | The user GID to use inside a container when [jsonnet](./jsonnet.md) `User()` function is used. |
        | `user.name` | string | The host username that will get converted to UID to use inside a container when [jsonnet](./jsonnet.md) `User()` function is used. |
        | `user.group` | string | The host groupname that will get converted to GID to use inside a container when [jsonnet](./jsonnet.md) `User()` function is used. |

    === "Advanced"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `build_image_tag_from_version` | boolean | **Deprecated**. Use `build_image_tag_from: version.version` instead. |
        | `compose.project_name` | string<br>`${core.project_name}` | docker-compose project name |
        | `compose.network_name` | string<br>`${docker.compose.project_name}_default` | The name of the default docker network for this docker-compose project.  |
        | `compose.file_version` | string<br>`3.7` | docker-compose.yml version to use  |
        | `compose.service_init` | boolean<br>`true` | Should `init: true` be added to all services ? |
        | `compose.service_context_root` | boolean<br>`false` | Should services build context match project home ? If false, it will match `directory` setting ? |
        | `directory` | string<br>`.docker` | The directory where container Dockerfile are stored. This should contain one subfolder per Dockerfile, containing the build context. |
        | `path_mapping` | dict[string, string] | Path mapping to apply on first part from docker-compose services volume mapping |

    === "Internal"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `interface` | string<br>`docker0` | Ethernet interface matching the docker network. |
        | `ip` | string<br>`<ip_address>` | IP adress matching the docker network. |
        | `reverse_proxy.network_id` | string<br>`reverse-proxy` | Network id used in generated `docker-compose.yml` configuration by [jsonnet](./jsonnet.md) feature. |
        | `reverse_proxy.network_names` | dict[string, string}<br>`{reverse-proxy: reverse-proxy}` | |
        | `reverse-proxy.type` | string<br>`traefik` (when available) | Type of reverse proxy used. |

!!! quote "Defaults"
    ```yaml
    docker:
      build_image_tag: null
      build_image_tag_from: false
      build_image_tag_from_version: false
      cache_from_image: false
      compose:
        file_version: '3.7'
        network_name: ddb-sonarqube_default
        project_name: ddb-sonarqube
        service_context_root: false
        service_init: true
      debug:
        disabled: false
        host: 172.17.0.1
      directory: .docker
      disabled: false
      disabled_services: []
      interface: docker0
      ip: 172.17.0.1
      jsonnet:
        binary_disabled: false
        virtualhost_disabled: false
      path_mapping: {}
      port_prefix: 304
      registry:
        name: null
        repository: null
      restart_policy: unless-stopped
      reverse_proxy:
        certresolver: null
        https: true
        network_id: reverse-proxy
        network_names:
          reverse-proxy: reverse-proxy
        redirect_to_https: null
        redirect_to_path_prefix: null
        type: traefik
      user:
        gid: 1000
        group: null
        group_to_gid: # dict mapping host group name to gid
        name: null
        name_to_uid: # dict mapping host user name to uid
        uid: 1000
    ```

!!! info "Creation of binaries"
    Whether you use `ddb.Binary()` in jsonnet template or manually add labels to `docker-compose.yml`, they 
    are converted into ddb configuration and shims are generated to run the declared binary as simple executable 
    command, thanks to [shell](shell.md) feature.