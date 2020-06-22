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
  disabled: false
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
    ext: test
    sub: projects
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
    project_home: /home/devbox/projects
  process: {}
  project:
    name: projects
docker:
  build_image_tag: null
  build_image_tag_from_version: true
  cache_from_image: false
  compose:
    network_name: projects_default
    project_name: projects
  debug:
    disabled: false
    host: 192.168.85.1
  directory: .docker
  disabled: false
  interface: docker0
  ip: 172.17.0.1
  path_mapping: {}
  port_prefix: 35
  registry:
    name: null
    repository: null
  restart_policy: 'no'
  reverse_proxy:
    network_id: reverse-proxy
    network_names:
      reverse-proxy: reverse-proxy
    type: traefik
  user:
    gid: 1001
    uid: 1001
file:
  disabled: false
  excludes:
  - '**/_*'
  - '**/.git'
  - '**/node_modules'
  - '**/vendor'
fixuid:
  disabled: false
  url: https://github.com/boxboat/fixuid/releases/download/v0.4/fixuid-0.4-linux-amd64.tar.gz
git:
  disabled: false
  fix_files_permissions: true
gitignore:
  disabled: false
jinja:
  disabled: false
  extensions:
  - .*
  - ''
  includes:
  - '*.jinja{.*,}'
  suffixes:
  - .jinja
jsonnet:
  disabled: false
  extensions:
  - .*
  - ''
  includes:
  - '*.jsonnet{.*,}'
  suffixes:
  - .jsonnet
permissions:
  disabled: false
  specs: null
shell:
  aliases: {} # Define aliases which will be available only in project context
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
smartcd:
  disabled: false
symlinks:
  disabled: false
  includes:
  - '*.dev{.*,}'
  suffixes:
  - .dev
traefik:
  certs_directory: /home/devbox/.docker-devbox/certs
  config_directory: /home/devbox/.docker-devbox/traefik/config
  disabled: false
  mapped_certs_directory: /certs
  ssl_config_template: "# This configuration file has been automatically generated\
    \ by ddb\n[[tls.certificates]]\n  certFile = \"%s\"\n  keyFile = \"%s\"\n"
version:
  disabled: false
ytt:
  args:
  - --ignore-unknown-comments
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