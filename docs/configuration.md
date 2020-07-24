Configuration
=============

**ddb** use **yaml configuration files**:

- `ddb.yml`, the main configuration file
- `ddb.local.yml`, the configuration file override.

Those files can be placed in those **directories**:

- Inside `~/.docker-devbox/ddb`
- Inside `~/.docker-devbox`
- Inside the project directory root

If many configuration files are found, they are **merged** with given filenames and directories order.

This configuration is **used internally** by feature actions, but is also injected as **context for each supported 
template engine**. You can add any data structure inside the configuration file so this data is available inside 
template engines.

!!! question "How to check effective configuration"
    You can run `ddb config` to view the merged effective configuration.
    
Each feature holds it's **own configuration** section under the **name of the feature**. For details about supported 
configuration settings, please check the documentation of related feature.

!!! info "Configuration and environment variables"
    To override any configuration setting, you may set an environment variable. 
    
    To convert the property name from dotted notation to environment variable, you should write in UPPERCASE, add 
    `DDB_` prefix replace `.` with `_`. For instance, `core.domain.ext` can be overriden with `DDB_CORE_DOMAIN_EXT` 
    environment variable.
    
    Variables lists can be referenced with `[0]`, `[1]`, ..., `[n]`
    
    When activating the environment `$(ddb activate)` with [shell feature (Environment activation)](#environment-activation), 
    the whole configuration is also exported as environment variables using the same naming convention.
    
!!! abstract "Default configuration"
    ```ddb config``` can provide default configuration if `ddb.yml` configuration file is empty.

    ```yml
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
        sub: ddb-quickstart
      env:
        available:
        - prod
        - stage
        - ci
        - dev
        current: dev
      os: posix
      path:
        ddb_home: /home/toilal/.docker-devbox/ddb
        home: /home/toilal/.docker-devbox
        project_home: /home/toilal/ddb-quickstart
      process: {}
      project:
        name: ddb-quickstart
    docker:
      build_image_tag: master
      build_image_tag_from_version: true
      cache_from_image: false
      compose:
        network_name: ddb-quickstart_default
        project_name: ddb-quickstart
      debug:
        disabled: false
        host: 172.17.0.1
      directory: .docker
      disabled: false
      interface: docker0
      ip: 172.17.0.1
      path_mapping: {}
      port_prefix: 507
      registry:
        name: null
        repository: null
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
      aliases: {}
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
      disabled: true
    symlinks:
      disabled: false
      includes:
      - '*.dev{.*,}'
      suffixes:
      - .dev
    traefik:
      certs_directory: /home/toilal/.docker-devbox/certs
      config_directory: /home/toilal/.docker-devbox/traefik/config
      disabled: false
      mapped_certs_directory: /certs
      ssl_config_template: "# This configuration file has been automatically generated\
        \ by ddb\n[[tls.certificates]]\n  certFile = \"%s\"\n  keyFile = \"%s\"\n"
    version:
      branch: master
      disabled: false
      hash: e78bccab1e980244c31592a923902525ede8985b
      short_hash: e78bcca
      tag: null
      version: null
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
