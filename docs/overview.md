Overview
===

Technology agnostic
-------------------

**ddb** is **not tied** to a particular language, framework or technical stack.

It's designed to **automate application and docker-compose configuration** on an environment, so you **forget 
about the docker hard stuff** while writing code, and so application can be deployed to stage and production 
environment with no changes on your sources.
    
Docker Devbox
---

Even if **ddb** can be used as a standalone tool, it has been designed with **[docker](https://www.docker.com/) and 
[docker-compose](https://docs.docker.com/compose/) in mind**. 

Many features requires some companion containers to run in background. Those containers have been **configured and 
packaged in [docker-devbox](https://github.com/inetum-orleans/docker-devbox)**, so you should really 
**consider installing** it.

[docker-devbox](https://github.com/inetum-orleans/docker-devbox) brings the following containers:

  - [traefik](https://containo.us/traefik/), to automatically **proxy services** provided by docker-compose using project
domain name virtualhost on **HTTP/80** and **HTTPS/443**, and **generate SSL certificates with Letsencrypt** (for public domain names).
  - [cfssl](https://github.com/cloudflare/cfssl), the Cloudflare's PKI and TLS toolkit, to **generate certificates for internal domains**.
  - [portainer](https://www.portainer.io/) to **manage containers** from a web browser.

Please read [docker-devbox README](https://github.com/inetum-orleans/docker-devbox/blob/master/README.md) to perform 
the installation properly.

!!! info "Eat your own dog food"
    docker-devbox containers are configured with **ddb** themselves.

Features, actions and events
----------------------------

**ddb** make use of **features** to perform it's magic.

Each feature holds it's own **configuration** and embeds one or many **actions**. An **action** configures
bindings between an **event** and a **function**, so when an **event** occurs, each binded **functions** are called.

An action's function implementation can also raise other events that will trigger other feature action functions, 
making **ddb** a reactive software.

!!! question "What occurs when running `ddb configure` ?"
    
    [configure is the most import command](./commands.md#ddb-configure) in ddb.

    When running `ddb configure` command, a bunch of **events** are triggered.
    
    Firstly, the command raise the `phase.configure` event, which is binded to the [file feature](./features/file.md).
    
    Secondly, [file feature](./features/file.md) scans files and triggers `file:found` event for each file in the 
    project directory.
    
    Thirdly, the [jsonnet](./features/jsonnet.md) feature, which is binded to `file:found` event with a filter to match
    `.jsonnet` file extension only, so that only those files are processed by the jsonnet template engine.
    
    Other features perform actions the same way, like [jinja](./features/jinja.md), [symlinks](./features/symlinks.md) 
    and [ytt](./features/ytt.md) features.
    
    Those actions raises other events, like `file:generated` for each generated files, that will be processed by the 
    [gitignore](./features/gitignore.md) feature to add generated files to ignore list.  
        
    And so on.
