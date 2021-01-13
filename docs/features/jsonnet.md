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

Run `ddb configure` to evaluate the template and generate target file.

Feature Configuration
---

A few configurations are available for this feature : 

- `disabled`: Definition of the status of the feature. If set to True, jsonnet templates will not be processed by 
               this feature.
    - type: boolean
    - default: False
              
- `suffixes`: Definition of the list of suffixes which will be used for detection of files that needs to be processed
              by the feature. 
    - type: array of strings
    - default: `[".jsonnet"]`
 
- `extensions`: TODO
    - type: array of strings
    - default: `['.*', '']`
 
- `includes`: TODO
    - type: array of strings
    - default: `['.*', '']`
 
- `excludes`: Define list of files to be excluded from jsonnet feature
    - type: array of strings
    - default: `[]`

!!! example "Configuration"
    ```yaml
    jsonnet:
      disabled: false
      extensions:
      - .*
      - ''
      includes:
      - '*.jsonnet{.*,}'
      suffixes:
      - .jsonnet
    ```

Docker-compose jsonnet library
---

Jsonnet feature provides a library with handful functions to help generate `docker-compose.yml`.

In order to make those available, you need to import the library:

```json
local ddb = import 'ddb.docker.libjsonnet';
```

### Compose

This function defines the minimal docker-compose configuration. 

!!! abstract "Parameters"
    - `network_names`: the network to add.
        - type: string|object
        - default: `docker.reverse_proxy.network_names` ddb configuration value
    - `version`: the docker-compose file version. 
        - type: string
        - default: `3.7`

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

### Build

This function generates a service configuration from a `Dockerfile` available in `.docker/<service>` directory.

It will also add the `init` to true and `restart` configurations for the service.

The `restart` configuration will be set with the `docker.restart_policy` ddb configuration.

If a docker registry is configured inside docker feature, `image` configuration will also be generated from the service 
name.

!!! abstract "Parameters"
    - `name`: 
    Generate the `build.context` configuration value by appending it to the `directory` parameter.
        - type: string
    - `image`:
    The name of the image. If docker registry is defined, it will generate the full uri for the image in the registry. 
        - type: string
        - default: `name` parameter.
    - `cache_from_image`: 
    If set to true and docker registry is defined, it will generate the `build.cache_from` configuration uri. 
        - type: boolean
        - default: `docker.cache_from_image` ddb configuration value
    - `directory`:
    Path to the directory in which images will be defined (one subfolder by image).
        - type: boolean
        - default: `docker.directory` ddb configuration value

!!! example "Example with a registry defined"
    ```json
    ddb.Build("db")
    ```
    will produce :
    ```yaml
    build:
      context: .docker/db
      cache_from: docker.io/project/db:master
    image: docker.io/project/db:master
    ```

### Image
This function generates a service configuration based on an external image.

It will also add the `init` to true and `restart` configurations for the service.

The `restart` configuration will be set with the `docker.restart_policy` ddb configuration.

!!! abstract "Parameters"
    - `image`: 
    The image to use
        - type: string


!!! example 
    ```json 
    ddb.Image("nginx:latest")
    ```
    will produce
    ```yaml
    image: nginx:latest
    ```

### ServiceName
This function generates the right service name for a service.

The main purpose is to have more easy way to manage Labels for traefik and easily add a middleware to a specific 
service.

It concatenates the given name with the name of the project.

!!! abstract "Parameters"
    - `name`: 
    The name of the service
        - type: string


!!! example
    With a project named "ddb" 
    ```json 
    ddb.ServiceName("test")
    ```
    will return
    ```yaml
    ddb-test


### Expose
This function generates an exposed port inside a service.

It use `docker.docker_prefix` to generate a fixed mapped port in order to avoid port collisions between projects.

!!! abstract "Parameters"
    - `container_port`:
    The port inside the container to expose
        - type: string or number
    
    - `host_port_suffix`:
    The end of the port inside the host, from `1 to 99`. If null, it use last 2 digits of `container_port` value.
        - type: string or number
      
    - `protocol`:
    The protocol to use. Can be null, `tcp` or `udp`.
        - type: string


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

    `147` is `docker.port_prefix` configuration value.

### User
This function generates the `user` configuration for a service.

In ddb, it is mainly use for `fixuid` automatic integration

!!! abstract "Parameters"
    - `uid`: The uid to use
        - type: string
        - default: `docker.user.uid` ddb configuration value
    - `gid`: The gid to use
        - type: string
        - default: `docker.user.gid` ddb configuration value

!!! example 
    ```json 
    ddb.User()
    ```
    will produce
    ```yaml
    user: 1000:1000
    ```

!!! info "userNameToUid/groupNameToGid to retrieve host uid/gid from names"
    ```json
    ddb.User(gid=ddb.groupNameToGid("docker"))
    ```
    will produce
    ```yaml
    user: 1000:998
    ```
    when `getent group docker` returns `docker:x:998:` on the host.
    
    It can be used when you need the container to access the docker socket through a volume mount.


### XDebug (PHP)
This function generates `environment` configuration used for XDebug (PHP Debugger).

If `docker.debug.disabled` is set to False, the function will return nothing.

It will use the following `ddb` configuration to generate appropriate `environment`:

* `core.project.name`: 
    * XDebug 2: set `serverName` and `idekey`; 
    * XDebug 3: set `XDEBUG_SESSION`;
* `docker.debug.host`: 
    * XDebug 2: set `remote_host`; 
    * XDebug 3: set `client_host`;

!!! abstract "Parameters"
    - `version`: The XDebug version to configure. If set to null, both XDebug 2 and 3 configurations will be set.
        - type: number (2 or 3) or null
        - default: null
    - `session`: The XDebug idekey to configure. By default project-name, but you can set explicitly this value to set env vars PHP_IDE_CONFIG and XDEBUG_CONFIG.
        - type: string
        - default: project-name
        
!!! example 
    ```json 
    ddb.Xdebug()
    ```
    will produce
    ```yaml
    environment:
      PHP_IDE_CONFIG: serverName=project-name
      XDEBUG_CONFIG: remote_enable=on remote_autostart=off idekey=project-name
        remote_host=192.168.85.1
    ```

### VirtualHost
This function generates service configuration used for reverse-proxy auto-configuration.

The output generated depends on the `docker.reverse_proxy.type` ddb configuration. Currently, only traefik is supported.
If this configuration is anything else, there will be no output.

!!! abstract "Parameters"
    - `port`:
    The port on which the trafic will be redirected.
        - type: string
    - `hostname`:
    The hostname that will be exposed.
        - type: string
    - `name`:
    A uniq name for the virtual host
        - type: string
    - `network_id`:
    The reverse-proxy network id.
        - type: string
        - default: `docker.reverse_proxy.network_id` ddb configuration
    - `certresolver`:
    If it is set to `letsencrypt` for instance, it will generate the certificate automatically.
    If it is set to null but `docker.reverse_proxy.certresolver` ddb configuration is sets, it will use the one configured.
    If nothing is sets, the reverse-proxy will use his internal one.
        - type: string|null
        - default: `docker.reverse_proxy.certresolver` ddb configuration
    - `router_rule`:
    You can add some custom router rule to the virtual host. For example, with Traefik you can set a wildcard for all 
    subdomain to be redirected to the current virtual host.
        - type: string|null
        - default: null
    - `redirect_to_https`:
    Set a forced redirection to https if set to true, or if set to null but the `docker.reverse_proxy.redirect_to_https` 
    ddb configuration is sets to true.
        - type: boolean|null
        - default: null
    - `path_prefix`:
    Add reverse proxy rules in order to use path prefix.
    For example, it allows you to use URL like https://your-app.test/service for your container exposure.
        - type: string|null
        - default: null
    - `redirect_to_path_prefix`:
    Redirect to defined path_prefix when accessing VirtualHost root path.
        - type: boolean|null
        - default: null

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

### Binary

Binary allow the creation of alias for command execution inside the service.

!!! abstract "Parameters"
    - `name`: the binary name. This will be the command you will enter in your terminal.
        - type: string
    - `workdir`: the default directory to execute the command into. In most case, it is the same as the service workdir.
        It will add the `--workdir=<workdir>` parameter to the docker-compose command
        - type: string|null
    - `args`: the command to execute inside the container
        - type: string|null
    - `options`: options to add to the docker-compose command.
        - type: string|null
    - `options_condition`: add a condition for the option to be added or not to the command.
        - type: string|null
    - `exe`: launch command with docker-compose `exec` instead of `run`.
        - type: boolean|null
    - `condition`: add a condition for the command to be enabled or not.
        - type: string|null

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

### BinaryLabels

BinaryLabels is mostly the same as [Binary](#binary) but output configuration without the `labels:` part, so you can add 
it directly to your own labels block.

!!! abstract "Parameters"
    - `name`: the binary name. This will be the command you will enter in your terminal.
        - type: string
    - `workdir`: the default directory to execute the command into. In most case, it is the same as the service workdir.
        It will add the `--workdir=<workdir>` parameter to the docker-compose command
        - type: string|null
    - `args`: the command to execute inside the container
        - type: string|null
    - `options`: options to add to the docker-compose command.
        - type: string|null
    - `options_condition`: add a condition for the option to be added or not to the command.
        - type: string|null

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

### BinaryOptions

BinaryOptions allow you to add options to service's binary previously declared.

!!! abstract "Parameters"
    - `name`: the binary name. This will be the command you will enter in your terminal.
        - type: string
    - `options`: options to add to the docker-compose command.
        - type: string|null
    - `options_condition`: add a condition for the option to be added or not to the command.
        - type: string|null
    
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

### BinaryOptionsLabels

BinaryOptionsLabels is mostly the same as [BinaryOptions](#binaryoptions) but output configuration without the 
`labels:` part, so you can add it directly to your own labels block.

!!! abstract "Parameters"
    - `name`: the binary name. This will be the command you will enter in your terminal.
        - type: string
    - `options`: options to add to the docker-compose command.
        - type: string|null
    - `options_condition`: add a condition for the option to be added or not to the command.
    - type: string|null
    
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

### env.index

This function allows you to get the index of the given environment in the list `core.env.available`.

If there is no parameter given, it provides the index of the current one. 

This can be used to add environment condition to a service activation, a specific configuration,... 

!!! abstract "Parameter"
    - `env`: the environment to search index of.
        - type: string|null
    
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

### env.is

This function allows you to check if the given environment is the current one, i.e. is equals to `core.env.current`.

It does not have any input parameter and returns boolean.

This can be used to add environment condition to a service activation, a specific configuration,... 
    
!!! example
    With the following configuration :  
    ```yml 
    core:
      env:
        current: dev
    ```
    
    - `ddb.env.is("prod")` will return false
    - `ddb.env.is("dev")` will return true

### path

Path is easy access to ddb configuration paths `core.path` values.

It is mostly used to add a folder as volume to service.

### JoinObjectArray

This function allows the generation of an array of object programmatically and then merge them which is not possible 
otherwise natively with jsonnet. 

!!! abstract "Parameters"
    - `object_array`: the array of objects to merge
        - type: array of objects
    
!!! example
    With the following jsonnet declaration :  
    ```jsonnet 
    local sites = ['www', 'api'];
    
    {
        "web": ddb.Build("web")
            + ddb.JoinObjectArray([ddb.VirtualHost("80", std.join('.', [site, "domain.tld"]), site) for site in sites])
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
    
### path.mapPath

TODO
