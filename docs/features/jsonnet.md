Jsonnet
===

[Jsonnet](https://jsonnet.org/) is embedded into ddb. You only have to use the right file extension for ddb to 
process it through the appropriate template engine.

Mainly used to generate `docker-compose.yml` configuration, you can still use it for any other json or yaml based 
templating purpose.

When a jsonnet template is processed, ddb use it's configuration as context, so you can use them as you need using 
jsonnet standard library function.

```json 
std.extVar("<name of the configuration variable>")
```

Run `ddb configure` to evaluate templates and generate target files.

!!! summary "Feature configuration (prefixed with `jsonnet.`)"
    === "Simple"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `disabled` | boolean<br>`false` | Should this feature be disabled ? |
        | `suffixes` | string[]<br>`['.jsonnet']` | A list of filename suffix to include. |
        | `extensions` | string[]<br>`['.*', '']` | A list of glob of supported extension. |
        | `excludes` | string[]<br>`[]` | A list of glob of filepath to exclude. |
        | `docker` | *Docker* | Docker related configuration.

    === "Advanced"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `includes` | string[]<br>`['*.jsonnet{.*,}']` | A list of glob of filepath to include. It is automatically generated from `suffixes` and `extensions`. |

!!! summary "Docker configuration (prefixed with `jsonnet.docker.`)"
    === "Simple"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `compose` | *Compose* | docker-compose defaults. |
        | `networks` | *Networks*  | `ddb.Networks()` defaults. |
        | `build` | *Build* | `ddb.Build()` defaults. |
        | `service` | *Service* | `ddb.Service()` defaults. |
        | `expose` | *Expose* | `ddb.Expose()` defaults. |
        | `registry` | *Registry* | Image registry settings. |
        | `user` | *User* | `ddb.User()` defaults. |
        | `binary` | *Binary* | `ddb.Binary()` defaults. |
        | `virtualhost` | *VirtualHost* | `ddb.VirtualHost()` defaults. |
        | `xdebug` | *XDebug* | `ddb.XDebug()` defaults. |

!!! summary "Docker Compose configuration (prefixed with `jsonnet.docker.compose.`)"
    === "Simple"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `project_name` | string | Docker compose project name |
        | `network_name` | string | Docker compose network name |
        | `version` | string<br>`3.7` | YAML File version to use  |
        | `excluded_services` | string[]<br>`[]` | Services to exclude (Block list). |
        | `included_services` | string[]<br>`[]` | Services to include (Allow list). |

!!! summary "Docker Networks configuration (prefixed with `jsonnet.docker.networks`)"
    === "Simple"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `names` | Dict[str, str] | Additional external networks |

!!! summary "Docker Build configuration (prefixed with `jsonnet.docker.build.`)"
    === "Simple"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `cache_from_image` | boolean<br>`False` | Add cache_from_image to configuration. |
        | `context.base_directory` | string<br>`.docker` | Base directory for build context. |
        | `context.use_project_home` | boolean<br>`False` | Use project home directory as build context. |
        | `image_tag_from` | boolean|string<br>`False` | Define if an image tag should be generated. If set to a string, it should match a configuration key to use as tag source, like `version.tag`, `version.branch`, `version.version`. |

    === "Advanced"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `image_tag` | string | Image tag value. |

!!! summary "Docker Service configuration (prefixed with `jsonnet.docker.service.`)"
    === "Simple"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `restart` | string<br>`unless-stopped`<br>`no` | The restart policy to use for all services. Can be `no`, `always`, `on-failure` or `unless-stopped`. Default value is `unless-stopped`, unless `core.env.current` is set to `dev` then it's set to `no`. |

    === "Advanced"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `init` | string | |

!!! summary "Docker Expose configuration (prefixed with `jsonnet.docker.expose.`)"
    | Property | Type | Description |
    | :---------: | :----: | :----------- |
    | `disabled` | boolean<br>`False` | Should `ddb.Expose()` perform nothing ? |
    | `port_prefix` | integer<br>`<based on core.project.name>` | Port prefix. |


!!! summary "Docker Mount configuration (prefixed with `jsonnet.docker.mount.`)"
    | Property | Type | Description |
    | :---------: | :----: | :----------- |
    | `disabled` | boolean<br>`False` | Should `ddb.Expose()` perform nothing ? |
    | `directory` | string | Base directory for all named volume mounts, absolute or relative to project home. |
    | `directories` | dict[string, string] | Directories for named volume mounts, absolute or relative to project home. key is the volume name, value is the local path to mount. |


!!! summary "Docker Registry configuration (prefixed with `jsonnet.docker.registry.`)"
    | Property | Type | Description |
    | :---------: | :----: | :----------- |
    | `name` | string | Registry name. |
    | `repository` | string | Registry repository. |


!!! summary "Docker User configuration (prefixed with `jsonnet.docker.user.`)"
    === "Simple"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `uid` | string | The user UID to use inside a container. |
        | `gid` | string | The user GID to use inside a container. |
        | `name` | string | The host username that will get converted to UID. |
        | `group` | string | The host groupname that will get converted to GID. |

    === "Internal"
        | `name_to_uid` | Dict[str, integer] | Mapping of user names to uid. |
        | `group_to_gid` | Dict[str, integer] | Mapping of group names to gid. |


!!! summary "Docker Binary configuration (prefixed with `jsonnet.docker.binary.`)"
    | Property | Type | Description |
    | :---------: | :----: | :----------- |
    | `disabled` | boolean<br>`False` | Should binary generation be disabled ? |
    | `global` | boolean | Should binaries be generated as global by default ? |


!!! summary "Docker VirtualHost configuration (prefixed with `jsonnet.docker.virtualhost.`)"
    === "Simple"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `https` | string | Should services be available as HTTPS ? If unset, it is available as both HTTP and HTTPS. |
        | `redirect_to_https` | string | Should services redirect to HTTPS when requested on HTTP ? |
        | `redirect_to_path_prefix` | string | Should services redirect to path_prefix when requested on root path ? |
        | `certresolver` | string | certresolver to use. `letsencrypt` is supported when using traefik reverse proxy. |

    === "Internal"
        | `type` | string<br>`traefik` (when available) | Type of reverse proxy to use. |
        | `network_id` | string<br>`reverse-proxy` | Network id used. |


!!! summary "Docker XDebug configuration (prefixed with `jsonnet.docker.xdebug.`)"
    === "Simple"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `disabled` | boolean<br>`false` | Should debug features be generated in `docker-compose.yml` by [jsonnet](./jsonnet.md) feature ? |
        | `host` | string<br>`${jsonnet}` | The host to connect back for debug features. |
        | `version` | string | XDebug version to configure (`2` or `3`). If unset, both XDebug 2 and 3 configurations will generated in a merged object. |
        | `session` | string<br>`${core.project.name}` | XDebug session (v3) and/or idekey/serverName (v2) to configure. You can set this value explicitly to set env vars `XDEBUG_SESSION` (v3) and/or `PHP_IDE_CONFIG`/`XDEBUG_CONFIG` (v2). |
        | `mode` | string<br>`debug` | XDebug mode (v3 only). |


## djp packages (ddb jsonnet packages)

You can include one or many **ddb jsonnet packages**, aka **djp**, into `ddb.Compose` configuration using `ddb.with()`.

More information: [Djp packages](../djp.md)

Docker-compose jsonnet library
---

Jsonnet feature provides a library with handful functions to help generate `docker-compose.yml`.

In order to make those available, you need to import the library:

```jsonnet
local ddb = import 'ddb.docker.libjsonnet';
```

### ddb.Compose()

This function defines the main entrypoint to generate a docker-compose configuration. 

!!! abstract "Parameters"
    | Property | Type | Description |
    | :---------: | :----: | :----------- |
    | `config` | object | Docker compose configuration |
    | `networks_names` | dict[str, str]<br>`${jsonnet.docker.networks.names}` | Network id to name mapping |
    | `version` | string<br>`${jsonnet.docker.compose.version}` | docker-compose.yml file version.  |

!!! example 
    ```json
    ddb.Compose()
    ```

    without any service configuration will produce

    ```yaml
    version: '3.7'
    networks:
      reverse-proxy:
        external: true
        name: reverse-proxy
    ```

!!! example 
    ```json
    ddb.Compose({
        services: {
            db: {
                image: "postgres"
            }
        }
    })
    ```

    with a configuration with produce

    ```yaml
    version: '3.7'
    networks:
      reverse-proxy:
        external: true
        name: reverse-proxy
    services:
      db:
        image: "postgres"
    ```

### ddb.Build()

This function generates a service configuration from a `Dockerfile` available in `.docker/<service>` directory.

If a docker registry is configured inside docker feature, `image` configuration will also be generated from the 
service name.

!!! abstract "Parameters"
    | Property | Type | Description |
    | :---------: | :----: | :----------- |
    | `name` | string | Generate a build configuration based on given name. |
    | `image` | string<br>`<name>` | The name of the image. If `registry_name` and/or `registry_name` settings are defined, it will generate the full image name.  |
    | `cache_from_image` | boolean<br>`${jsonnet.docker.build.cache_from_image}` | If set to true and docker registry is defined, it will generate the `build.cache_from` configuration uri.  |
    | `context_base_directory` | boolean<br>`${jsonnet.docker.build.context.base_directory}` | Build context base directory. |
    | `context_use_project_home` | boolean<br>`${jsonnet.docker.build.context.use_project_home}` | Use project home directory as context. |
    | `restart` | string<br>`${jsonnet.docker.service.restart}` | Service restart policy. |
    | `init` | boolean<br>`${jsonnet.docker.service.init}` | Service init. |
    | `registry_name` | string<br>`${jsonnet.docker.registry.name}` | Name of the docker image registry. |
    | `registry_repository` | string<br>`${jsonnet.docker.registry.repository}` | Repository in the docker image registry. |
    | `image_tag` | boolean|string<br>`${jsonnet.docker.build.image_tag}` | If false, tag is not set. If `true`, tag is set according to `jsonnet.docker.build.image_tag_from` value. If `string` value, use the exact given string as tag. |


!!! example "Example with a registry defined"
    if ddb.yml contains the following

    ```
    jsonnet:
      docker:
        registry:
          name: docker.io
          repository: project
        build:
          image_tag_from: True
    ```

    ```json
    ddb.Build("db")
    ```

    will produce

    ```yaml
    build:
      context: .docker/db
      cache_from: docker.io/project/db:master
    image: docker.io/project/db:master
    ```

### ddb.Image()
This function generates a service configuration based on an external image.

It will also add the `init` to true and `restart` configurations for the service.

The `restart` configuration will be set with the `jsonnet.docker.service.restart` ddb configuration.

!!! abstract "Parameters"
    | Property | Type | Description |
    | :---------: | :----: | :----------- |
    | `image` | string<span style="color: red">*</span> | The name of the image to use.  |
    | `restart` | string<br>`${jsonnet.docker.service.restart}` | Service restart policy. |
    | `init` | boolean<br>`${jsonnet.docker.service.init}` | Service init. |


!!! example 
    ```json 
    ddb.Image("nginx:latest")
    ```

    will produce

    ```yaml
    image: nginx:latest
    restart: no
    init: true
    ```

### ddb.Expose()
This function generates an exposed port inside a service.

It use `jsonnet.docker.expose.port_prefix` to generate a fixed mapped port in order to avoid port collisions between projects.

!!! abstract "Parameters"
    | Property | Type | Description |
    | :---------: | :----: | :----------- |
    | `container_port` | string\|integer<span style="color:red">*</span> | Container port number to expose. |
    | `host_port_suffix` | string | End of the mapped port on host. from `1 to 99`. If `null`, use last 2 digits of `container_port` value. |
    | `protocol` | string | The protocol to use. Can be `null`, `tcp` or `udp`.  |
    | `port_prefix` | string\|integer<br>`${jsonnet.docker.expose.port_prefix}` | Port prefix. |

!!! example
    ```json
    ddb.Expose(21) +
    ddb.Expose(22, null, "udp") +
    ddb.Expose(23, 99, "tcp")
    ```

    will produce

    ```yaml
    ports:
      - '14721:21'
      - '14722:22/udp'
      - '14799:23/tcp'
    ```

    `147` is `jsonnet.docker.expose.port_prefix` configuration value.


!!! tip "You can expose the same container port many times"
    To resolve published port collisions, when a published port is already consumed by another ddb.Expose() invocation, 
    ddb automatically increments the published port until it's available.

    ```json
    ddb.Expose(21) +
    ddb.Expose(21) +
    ```

    will produce

    ```yaml
    ports:
      - '14721:21'
      - '14722:21'
    ```

    `147` is `jsonnet.docker.expose.port_prefix` configuration value.

### ddb.User()
This function generates the `user` configuration for a Service.

In ddb, it is mainly use for [fixuid](./fixuid.md) automatic integration

!!! abstract "Parameters"
    | Property | Type | Description |
    | :---------: | :----: | :----------- |
    | `uid` | string<br>`${jsonnet.docker.user.uid}`<br>`${~jsonnet.docker.user.name}` | UID of user running the container. |
    | `gid` | string<br>`${jsonnet.docker.user.gid}`<br>`${~jsonnet.docker.user.group}` | GID of user running the container. |


!!! example 
    ```json 
    ddb.User()
    ```

    will produce

    ```yaml
    user: 1000:1000
    ```

!!! tip "`userNameToUid` and `groupNameToGid` to retrieve host uid/gid from names"
    ```json
    ddb.User(gid=ddb.groupNameToGid("docker"))
    ```

    will produce

    ```yaml
    user: 1000:998
    ```

    when `getent group docker` returns `docker:x:998:` on the host.
    
    It can be used when you need the container to access the docker socket through a volume mount.


### ddb.VirtualHost()
This function generates service configuration used for reverse-proxy auto-configuration.

The output generated depends on the `jsonnet.docker.virtualhost.type` ddb configuration. Currently, only traefik is supported.
If this configuration is anything else, there will be no output.

!!! abstract "Parameters"
    | Property | Type | Description |
    | :---------: | :----: | :----------- |
    | `port` | string<span style="color: red">*</span> | HTTP port inside the container. |
    | `hostname` | string<span style="color: red">*</span> | Hostname that will be exposed. |
    | `name` | string | Unique name for this VirtualHost. |
    | `network_id` | string<br>`${jsonnet.docker.virtualhost.network_id}` | The reverse-proxy network id. |
    | `certresolver` | string<br>`${jsonnet.docker.virtualhost.certresolver}` | certresolver to use inside reverse proxy (traefik). `letsencrypt` is supported when using `traefik` feature. |
    | `router_rule` | string |  |
    | `https` | string<br>`${jsonnet.docker.virtualhost.https}` | Should service be available as HTTPS ? If unset, it is available as both HTTP and HTTPS. |
    | `redirect_to_https` | string<br>`${jsonnet.docker.virtualhost.redirect_to_https}` | Should service redirect to HTTPS when requested on HTTP ? |
    | `path_prefix` | string | Path prefix of this virtualhost |
    | `redirect_to_path_prefix` | boolean | Redirect to configured path prefix |

!!! example "Example with traefik as reverse proxy"
    ```json 
    ddb.VirtualHost("80", "your-project.test", "app")
    ```

    will produce

    ```yaml
    labels:
      traefik.enable: 'true'
      traefik.http.routers.your-project-app-tls.rule: Host(`your-project.test`)
      traefik.http.routers.your-project-app-tls.service: your-project-app
      traefik.http.routers.your-project-app-tls.tls: 'true'
      traefik.http.routers.your-project-app.rule: Host(`your-project.test`)
      traefik.http.routers.your-project-app.service: your-project-app
      traefik.http.services.your-project-app.loadbalancer.server.port: '80'
    networks:
    - default
    - reverse-proxy
    ```

### ddb.Binary()

Binary allow the creation of alias for command execution inside the service.

!!! abstract "Parameters"
    | Property | Type | Description |
    | :---------: | :----: | :----------- |
    | `name` | string<span style="color: red">*</span> | Binary name. This will be the command you type in shell (see [shell](./shell.md) feature). |
    | `workdir` | string | Default container directory to run the command. In most case, it should match the service workdir. |
    | `args` | string<br>`<name>` | Command to execute inside the container. |
    | `options` | string | Options to add to the command. |
    | `options_condition` | string | Add a condition to be evaluated to make `options` optional. If condition is defined and evaluated, `options` are not added to the command. |
    | `exe` | boolean<br>`false` | Launch command with docker-compose `exec` instead of `run`. |
    | `entrypoint` | string | Override entrypoint for this binary. |
    | `global` | boolean<br>`false` | Creates a global binary shim in `~/.docker-devbox/.bin` directory so it can be runned everywhere. |
    | `condition` | string |  Add a condition for the command to be enabled. If condition is defined and evaluated to false, command won't be used by [run](./run.md) feature. |

!!! example 
    ```json 
    ddb.Binary("npm", "/app", "npm", "--label traefik.enable=false", '"serve" not in args')
    ```

    will produce

    ```yaml
    labels:
        ddb.emit.docker:binary[npm](args): npm
        ddb.emit.docker:binary[npm](name): npm
        ddb.emit.docker:binary[npm](options): --label traefik.enable=false
        ddb.emit.docker:binary[npm](options_condition): '"serve" not in args'
        ddb.emit.docker:binary[npm](workdir): /app
    ```

!!! tip "Register the same command many times"
    You may want is some projects to have many binaries defined for the same command, i.e many version of `composer` or 
    `npm`.

    It is possible to implement a condition on each Binary in order to enable one binary in a project directory, and 
    another one in another project directory.

    Each binary sharing the same name should be defined in distinct services though, as it doesn't make sense to define 
    the same command on the same service.

    You can find more information in [run](./run.md) feature: [Register many binaries for the same command](./run.md#register-many-binaries-for-the-same-command).

### ddb.XDebug() (PHP)
This function generates `environment` configuration used for XDebug (PHP Debugger).

If `jsonnet.docker.xdebug.disabled` is set to `true`, the function returns an empty object.

It will use the following `ddb` configuration to generate appropriate `environment`:

* `core.project.name`: 
    * XDebug 2: set `serverName` and `idekey`
    * XDebug 3: set `XDEBUG_SESSION`
* `jsonnet.docker.xdebug.host`: 
    * XDebug 2: set `remote_host`
    * XDebug 3: set `client_host`

!!! abstract "Parameters"
    | Property | Type | Description |
    | :---------: | :----: | :----------- |
    | `version` | string<br>`${jsonnet.docker.xdebug.version}` | XDebug version to configure (`2` or `3`). If unset, both XDebug 2 and 3 configurations will generated in a merged object. |
    | `session` | string<br>`${jsonnet.docker.xdebug.session}` | XDebug session (v3) and/or idekey/serverName (v2) to configure. You can set this value explicitly to set env vars `XDEBUG_SESSION` (v3) and/or `PHP_IDE_CONFIG`/`XDEBUG_CONFIG` (v2). |
    | `mode` | string<br>`${jsonnet.docker.xdebug.mode}` | XDebug mode (v3 only). |
        
!!! example 
    ```json
    ddb.Xdebug()
    ```

    will produce

    ```yaml
    environment:
      PHP_IDE_CONFIG: serverName=project-name
      XDEBUG_CONFIG: remote_enable=on remote_autostart=off idekey=project-name remote_host=192.168.85.1
    ```

### ddb.env.is()

This function allows you to check if the given environment is the current one, i.e. is equals to `core.env.current`.

It does not have any input parameter and returns boolean.

This can be used to add environment condition to a service activation, a specific configuration,... 

!!! abstract "Parameters"
    | Property | Type | Description |
    | :---------: | :----: | :----------- |
    | `env` | string | Environment name to verify. |


!!! example
    With the following configuration :  
    ```yml 
    core:
      env:
        current: dev
    ```

    - `ddb.env.is("prod")` => `false`
    - `ddb.env.is("dev")` => `true`

### ddb.env.current / ddb.env.available

Shortcuts for `std.extVar("core.env.current")` and `std.extVar("core.env.available")`.

### ddb.projectName / ddb.domain

Shortcuts for `std.extVar("core.project.name")`, `std.extVar("core.domain.value")`

### ddb.subDomain()

Builds a subdomain string from default domain name of another domain name.

!!! example
    With the following configuration :  
    ```yml 
    core:
      domain:
        sub: domain
        ext: tld
    ```

    - `ddb.subDomain("mailcatcher")` => `mailcatcher.domain.tld`
    - `ddb.subDomain("mailcatcher", "inetum.world")` => `mailcatcher.inetum.world`

## Advanced functions

Those functions are for advanced configuration and should not be used in most common cases.

??? info "Advanced"
    ### ddb.ServiceName()
    This function generates the right service name for a service.

    The main purpose is to have more easy way to manage Labels for traefik and easily add a middleware to a specific 
    service.

    It concatenates the given name with `${core.project.name}`.

    !!! abstract "Parameters"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `name` | string<span style="color: red">*</span> | Name of the service. |

    !!! example
        With a project named "ddb" 
        ```json 
        ddb.ServiceName("test")
        ```
        will return
        ```yaml
        ddb-test
    
    ### ddb.BinaryLabels()
    
    BinaryLabels is mostly the same as [Binary](#binary) but output configuration without the `labels:` part, so you can add 
    it directly to your own labels block.
    
    !!! abstract "Parameters"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `name` | string<span style="color: red">*</span> | Binary name. This will be the command you type in shell (see [shell](./shell.md) feature). |
        | `workdir` | string | Default container directory to run the command. In most case, it should match the service workdir. |
        | `args` | string<br>`<name>` | Command to execute inside the container. |
        | `options` | string | Options to add to the command. |
        | `options_condition` | string | Add a condition to be evaluated to make `options` optional. If condition is defined and evaluated, `options` are not added to the command. |
    
    !!! example 
        ```json 
        ddb.BinaryLabels("npm", "/app", "npm", "--label traefik.enable=false", '"serve" not in args')
        ```

        will produce

        ```yaml
        ddb.emit.docker:binary[npm](args): npm
        ddb.emit.docker:binary[npm](name): npm
        ddb.emit.docker:binary[npm](options): --label traefik.enable=false
        ddb.emit.docker:binary[npm](options_condition): '"serve" not in args'
        ddb.emit.docker:binary[npm](workdir): /app
        ```
    
    ### ddb.BinaryOptions()
    
    BinaryOptions allow you to add options to service's binary previously declared.
    
    !!! abstract "Parameters"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `name` | string<span style="color: red">*</span> | Binary name. This will be the command you type in shell (see [shell](./shell.md) feature). |
        | `options` | string | Options to add to the command. |
        | `options_condition` | string | Add a condition to be evaluated to make `options` optional. If condition is defined and evaluated, `options` are not added to the command. |

        
    !!! example 
        ```json 
        ddb.BinaryOptions("npm", "--label traefik.enable=false", '"serve" not in args')
        ```

        will produce

        ```yaml
        labels:
            ddb.emit.docker:binary[npm](options): --label traefik.enable=false
            ddb.emit.docker:binary[npm](options_condition): '"serve" not in args'
        ```
    
    ### ddb.BinaryOptionsLabels()
    
    BinaryOptionsLabels is mostly the same as [BinaryOptions](#binaryoptions) but output configuration without the 
    `labels:` part, so you can add it directly to your own labels block.
    
    !!! abstract "Parameters"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `name` | string<span style="color: red">*</span> | Binary name. This will be the command you type in shell (see [shell](./shell.md) feature). |
        | `options` | string | Options to add to the command. |
        | `options_condition` | string | Add a condition to be evaluated to make `options` optional. If condition is defined and evaluated, `options` are not added to the command. |

        
    !!! example 
        ```json 
        ddb.BinaryOptions("npm", "--label traefik.enable=false", '"serve" not in args')
        ```

        will produce

        ```yaml
        labels:
            ddb.emit.docker:binary[npm](options): --label traefik.enable=false
            ddb.emit.docker:binary[npm](options_condition): '"serve" not in args'
        ```

    
    ### ddb.path
    
    Path is easy access to ddb configuration paths `core.path` values.
    
    It is mostly used to add a folder as volume to service.

    ### ddb.env.index()
    
    This function allows you to get the index of the given environment in the list `core.env.available`.
    
    If there is no parameter given, it provides the index of the current one. 
    
    This can be used to add environment condition to a service activation, a specific configuration,... 

    !!! abstract "Parameters"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `env` | string | Environment name to verify. |

        
    !!! example
        With the following configuration :  
        ```yml 
        core:
          env:
            available:
            - prod
            - stage
            - ci
            - dev
            current: dev
        ```
        
        - `ddb.env.index()` will return 3
        - `ddb.env.index("ci")` will return 2

    
    ### ddb.mergeAll()
    
    This function merge an array of objects.

    !!! abstract "Parameters"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `object_array` | dict[] | the array of objects to merge. |

    !!! example
        With the following jsonnet declaration :  
        ```jsonnet 
        local sites = ['www', 'api'];
        
        {
            "web": ddb.Build("web")
                + ddb.mergeAll([ddb.VirtualHost("80", std.join('.', [site, "domain.tld"]), site) for site in sites])
                + {
                    "volumes": [
                        ddb.path.project + "/.docker/web/nginx.conf:/etc/nginx/conf.d/default.conf:rw",
                        ddb.path.project + ":/var/www/html:rw"
                    ]
                }
        }
        ```
        
        The result will be
        ```yaml
        labels: 
          traefik.enable: "true"
          traefik.http.routers.your-project-api-tls.rule: Host(`api.domain.tld`)
          traefik.http.routers.your-project-api-tls.service: your-project-api
          traefik.http.routers.your-project-api-tls.tls: "true"
          traefik.http.routers.your-project-api.rule: Host(`api.domain.tld`)
          traefik.http.routers.your-project-api.service: your-project-api
          traefik.http.services.your-project-api.loadbalancer.server.port: '80'
          traefik.http.routers.your-project-www-tls.rule: Host(`www.domain.tld`)
          traefik.http.routers.your-project-www-tls.service: your-project-www
          traefik.http.routers.your-project-www-tls.tls: "true"
          traefik.http.routers.your-project-www.rule: Host(`www.domain.tld`)
          traefik.http.routers.your-project-www.service: your-project-www
          traefik.http.services.your-project-www.loadbalancer.server.port: '80'
        ```
        
    ### ddb.path.mapPath()
    
    Get the mapped value of a given filepath according to mappings configured in `docker.path_mapping`.

    !!! abstract "Parameters"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `path` | string | Source path. |

    ### ddb.File
    
    Wrap a string matching a Filesystem path into a File object containing `name` and `parent`. `name` match the filename of 
    this path, and `parent` is another File object matching the parent path.
    
    !!! example
        - `ddb.File(".docker/postgres/djp.libsonnet")` => `{name: 'djp.libjsonnet', parent: {name: postgres, parent: {name: .docker}}}`
    
        
