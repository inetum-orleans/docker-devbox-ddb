Jsonnet
===

[Jsonnet](https://jsonnet.org/) is embedded into ddb. You only have to use the right file extension for ddb to 
process it through the appropriate template engine.

Mainly used for docker-compose.yml generation, you can use it for any file generation you want.

When jsonnet templates are processed, ddb inject all his configuration into the template, so you can use them as 
you need using jsonnet standard library function : 
```jsonnet 
std.extVar("<name of the configuration variable>")
```

Functions for docker-compose templates
---

Jsonnet feature provides a handful list of functions to help generation of docker-compose.

In order to make those available, you need to include the library:
```jsonnet
local ddb = import 'ddb.docker.libjsonnet';
```

This will provide you the following functions to simplify `docker-compose.yml` file generation.

### Compose

This function defines global docker-compose configurations elements. 

Two parameters are available : 

- `network_names`: the network to add.
    - type: string|object
    - default value: `docker.reverse_proxy.network_names` ddb configuration value
- `version`: the docker-compose file version. 
    - type: string
    - default value: `3.7`

It defines the following settings :

- `version`: 
set with the function parameter `version`.
- `volumes`: 
set with named volumes retrieved from defined services.
- `networks`: 
set with external networks retrieved from defined services and the function parameter `network_names`.

Example output: 
```yaml
version: '3.7'
networks:
  reverse-proxy:
    external: true
    name: reverse-proxy
```

### Build
This function generates the `build` configuration for a service and `image` if docker registry is defined.

Four parameters are available :

- `name`: 
Generate the `build.context` configuration value by appending it to the `directory` parameter.
    - type: string
- `image`:
The name of the image. If docker registry is defined, it will generate the full uri for the image in the registry. 
    - type: string
    - default value: `name` parameter.
- `cache_from_image`: 
If set to true and docker registry is defined, it will generate the `build.cache_from` configuration uri. 
    - type: boolean
    - default value: `docker.cache_from_image` ddb configuration value
- `directory`:
Path to the directory in which images will be defined (one subfolder by image).
    - type: boolean
    - default value: `docker.directory` ddb configuration value

Example output:
```yaml
build:
  context: .docker/db
  cache_from: docker.io/project/db:master
image: docker.io/project/db:master
```

### Image
This function generates the `image` configuration for a service.

Only one parameter are available :

- `image`: 
The image to use
    - type: string

Example output:
```yaml
image: nginx
```

### User
This function generate the `user` configuration for a service.

In ddb, it is mainly use for `fixuid` automatic integration

Two parameters are available :

- `uid`: 
The uid to use
    - type: string
    - default : `docker.user.uid` ddb configuration value
- `gid`: 
The gid to use
    - type: string
    - default : `docker.user.gid` ddb configuration value

Example output:
```yaml
user: 1000:1000
```

### XDebug
This function generate `environment` configuration used for PHP XDebug.

There is not parameter, but it will generate `PHP_IDE_CONFIG` and `XDEBUG_CONFIG` if `docker.debug.disabled` 
ddb configuration is set to `False`.

For the `serverName` and `idekey`, it will be set with the ddb configuration `core.project.name`.

For the `remote_host`, it will be set with the ddb configuration `docker.debug.host`.

Example output:
```yaml
environment:
  PHP_IDE_CONFIG: serverName=project-name
  XDEBUG_CONFIG: remote_enable=on remote_autostart=off idekey=project-name
    remote_host=192.168.85.1
```

### VirtualHost
This function generate service configuration used for reverse-proxy auto-configuration.

The output generated depends on the `docker.reverse_proxy.type` ddb configuration. Currently, only traefik is supported.
If this configuration is anything else, there will be no output.

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

Example output with Traefik:
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

Feature Configuration
---

A few configurations are available for this features : 
- `disabled`: Definition of the status of the feature. If set to True, jsonnet templates will not be processed by 
               this feature.
    - type: boolean
    - default value: False
              
- `suffixes`: Definition of the list of suffixes which will be used for detection of files that needs to be processed
              by the feature. 
    - type: array of strings
    - default value: `[".jsonnet"]`
 
- `extensions`: TODO : Explain the use of extensions
    - type: array of strings
    - default value: `['.*', '']`
 
- `includes`: TODO : Explain the use of includes
    - type: array of strings
    - default value: `['.*', '']`
 
- `excludes`: Define list of files to be excluded from jsonnet feature
    - type: array of strings
    - default value: `[]`

Here is the default configuration that you can retrieve from ```ddb config``` commands and override in your `ddb.yaml`
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

TODO 
---
```jsonnet
{
    Binary: Binary,
    BinaryLabels: BinaryLabels,
    BinaryOptions: BinaryOptions,
    BinaryOptionsLabels: BinaryOptionsLabels,
    Volumes: Volumes,
    env: {
      index: envIndex,
      is: envIs
    },
    path: path
}
```