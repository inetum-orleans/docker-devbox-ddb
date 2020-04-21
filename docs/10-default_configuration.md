Default Configuration
===

docker-devbox-ddb provide a complete configuration from scratch. 
You can see the current configuration by launching the given command : 
```
ddb config
```

If you want to globally override any of the default configuration, you need to create a ddb.yaml file in one of the following folders : 
- ddb_home
- home
- project_home

The value of those folder are available in configuration under ```core.path```

The most common values to override are the following : 
```yaml
core:
  domain:
    sub: docker-devbox-ddb # The subdomain to use for the project. By default, it will be the name of the project directory
  debug:
    host: 192.168.72.1 # IP of the computer debugging the project
``` 

Here is the list of default configuration provided by docker-devbox-ddb : 
```yaml
binary:
  disabled: false # Disable the binary generation for the project and the run option
certs:
  cfssl:
    append_ca_certificate: true
    server:
      host: localhost
      port: 7780
      ssl: false
      verify_cert: true
    writer:
      filenames:
        certificate: '%s.crt'
        certificate_der: '%s.crt.der'
        certificate_request: '%s.csr'
        certificate_request_der: '%s.csr.der'
        private_key: '%s.key'
  destination: .certs
  disabled: false
  type: cfssl
copy:
  disabled: false
core:
  disabled: false
  domain:
    ext: test # The base domain extension used for traefik DNS registration
    sub: docker-devbox-ddb # The subdomain to use for the project. By default, it will be the name of the project directory
  env:
    available: # List of available environments
    - prod
    - stage
    - ci
    - dev
    current: dev # Current active environment
  os: posix
  path:
    ddb_home: /home/docker/.docker-devbox/ddb
    home: /home/docker/.docker-devbox
    project_home: /home/docker/projects/docker-devbox-ddb # The directory of the project you are working on
  project:
    name: docker-devbox-ddb # The name of the project. By default, it will be the name of the project directory
docker:
  cache_from_image: false
  compose:
    args: []
    bin: docker-compose
    network_name: docker-devbox-ddb_default # The docker network name for the project
    project_name: docker-devbox-ddb # The project name used in docker-compose
  debug:
    disabled: false # Disable the debug mod for the project (disable xDebug for instance)
    host: 192.168.72.1 # IP of the computer debugging the project
  directory: .docker
  disabled: false
  interface: docker0
  ip: 172.17.0.1
  path_mapping: {}
  port_prefix: 70 # The port prefix used in docker-compose port exposition
  registry: # The registry used for image storage
    name: null
    repository: null
  restart_policy: 'no' # The restart_policy applied
  reverse_proxy:
    network_id: reverse-proxy # The id of the reverse-proxy network
    network_names:
      reverse-proxy: reverse-proxy
    type: traefik # The type of the reverse-proxy network
  user:
    gid: 1001 # The id of the current user
    uid: 1001 # The gid of the current user
file:
  disabled: false
  excludes:
  - '**/_*'
  - '**/.git'
  - '**/node_modules'
  - '**/vendor'
fixuid:
  disabled: false # Disable fixuid automatic integration in the Dockerfile
  url: https://github.com/boxboat/fixuid/releases/download/v0.4/fixuid-0.4-linux-amd64.tar.gz # The url of fixuid used
gitignore:
  disabled: false # Disable the automatic update of gitignore
jinja:
  disabled: false # Disable Jinja template engine
  extensions:
  - .*
  - ''
  includes:
  - '*.jinja{.*,}'
  suffixes:
  - .jinja
jsonnet:
  disabled: false # Disable jsonnet template engine
  extensions:
  - .*
  - ''
  includes:
  - '*.jsonnet{.*,}'
  suffixes:
  - .jsonnet
plugins:
  disabled: false
shell:
  disabled: false
  envignore:
  - PYENV_*
  - _
  - PS1
  - PS2
  - PS3
  - PS4
  path:
    directories:
    - .bin
    - bin
    prepend: true
  shell: bash
symlinks:
  disabled: false
  includes:
  - '*.dev{.*,}'
  suffixes:
  - .dev
traefik:
  certs_directory: /home/docker/.docker-devbox/certs
  config_directory: /home/docker/.docker-devbox/traefik/config
  disabled: false # Disable automatic traefik integration
  mapped_certs_directory: /certs
  ssl_config_template: "# This configuration file has been automatically generated\
    \ by ddb\n[[tls.certificates]]\n  certFile = \"%s\"\n  keyFile = \"%s\"\n"
ytt:
  args:
  - --ignore-unknown-comments
  bin: ytt
  depends_suffixes:
  - .data
  - .overlay
  disabled: false
  extensions:
  - .yaml
  - .yml
  - ''
  includes:
  - '*.ytt{.yaml,.yml,}'
  keywords:
  - and
  - elif
  - in
  - or
  - break
  - else
  - lambda
  - pass
  - continue
  - for
  - load
  - return
  - def
  - if
  - not
  - while
  - as
  - finally
  - nonlocal
  - assert
  - from
  - raise
  - class
  - global
  - try
  - del
  - import
  - with
  - except
  - is
  - yield
  keywords_escape_format: '%s_'
  suffixes:
  - .ytt
```