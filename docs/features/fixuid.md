Fixuid
===

One common pitfall when working with Docker is file permission management of mounted volumes.

Those permission issues are related to the way docker works and cannot really be fixed once for all.

To help developer fixing permission issues, [fixuid](https://github.com/boxboat/fixuid) is auto-configured by ddb when
a `fixuid.yml` file is available in docker build context.

!!! summary "Feature configuration (prefixed with `fixuid.`)"
    === "Simple"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `disabled` | boolean<br>`false` | Should this feature be disabled ? |
        
    === "Internal"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `url` | string<br>`https://github.com/boxboat/fixuid/releases/download/v0.5/fixuid-0.5-linux-amd64.tar.gz` | URL to download the fixuid distribution binary. |

Automatic configuration
---

In order to benefit from this feature, few steps are require. 

First, you need to create the `fixuid.yml` configuration file next to `Dockerfile.jinja`. For this feature
to work properly, you must use a template feature for your Dockerfile, like [Jinja](./jinja.md). 

In this `fixuid.yml` configuration file, you have to define three settings: 

- `user`: the user inside the container which is allowed to run command and access files.
- `group`: the group inside the container which is allowed to run command and access files.
- `paths`: the list of paths inside the container where permissions will be fixed. Volumes mount point must also be listed.

For more details on this configuration, please refer to the 
[fixuid documentation](https://github.com/boxboat/fixuid#specify-paths-and-behavior-across-devices).

!!! example "Example : A posgresql fixuid configuration"
    ```yaml
    user: postgres
    group: postgres
    paths:
      - /
      - /var/lib/postgresql/data
    ``` 
    
Then, in your `docker-compose.yml.jsonnet`, you should use [ddb.User()](jsonnet.md#user) in order to map your local 
user to the container. 
 
Finally, run the `ddb configure` command to generate `Dockerfile`. Instructions related to fixuid should have 
been generated. The entrypoint is changed to run fixuid before the default entrypoint.

!!! example "Example with PostgreSQL"
    ```dockerfile
    FROM postgres

    # Mount this volume to help loading/exporting dumps
    RUN mkdir /workdir
    VOLUME /workdir
    
    USER postgres
    ```

    Generates the following when `fixuid.yml` file is available in the `Dockerfile` directory.

    ```dockerfile
    FROM postgres
    
    # Mount this volume to help loading/exporting dumps
    RUN mkdir /workdir
    VOLUME /workdir

    USER postgres

    ADD fixuid.tar.gz /usr/local/bin
    RUN chown root:root /usr/local/bin/fixuid && chmod 4755 /usr/local/bin/fixuid && mkdir -p /etc/fixuid
    COPY fixuid.yml /etc/fixuid/config.yml
    USER postgres
    ENTRYPOINT ["fixuid", "-q", "docker-entrypoint.sh"]
    CMD ["postgres"]
    ```
    
    With this configuration, you should be able to generate a dump from the container as your own user instead of root.

!!! question "Why should I use `.jinja` extension for my `Dockerfile` ?"
    You should always use `.jinja` when declaring a Dockerfile to benefits of `fixuid` feature.    

    Using `fixuid` feature updates `Dockerfile` to add the instructions needed for fixuid. That's why you should 
    use a template source instead, for this to be generated again on each `ddb` configure command. 

    The `Dockerfile` will be automatically ignored by git thanks to [gitignore](./gitignore.md) feature.

!!! warning "If you are not using `jsonnet` for `docker-compose.yml`"    
    In `docker-compose.yml`, you will need to add the configuration `user` to the service using this 
    docker container.

    You will need to set it manually with the `uid` and `gid` of the host user which will run the container and execute 
    commands.
    
    As many other ddb features are available through [jsonnet feature](./jsonnet.md), you should really consider using 
    it. This will help you to build simpler, shorter and smarter `docker-compose` configuration.

!!! info "Disable or customize fixuid automatic configuration"

    You may need to disable fixuid automatic configuration. Use the following comments in your Dockerfile.jinja.

    - `# fixuid-disable`: Disable both download of fixuid.tar.gz and whole auto-configuration. Use this to disable fixuid totally for this Dockerfile.
    - `# fixuid-manual`: Only keep download of fixuid.tar.gz. Use this to configure fixuid totally manually in the Dockerfile.
    - `# fixuid-manual-install`: Keep download of fixuid.tar.gz and auto-configuration of ENTRYPOINT. You still have to install fixuid manually in the Dockerfile.
    - `# fixuid-manual-entrypoint`: Keep download of fixuid.tar.gz and installation of required files. You still have to invoke fixuid manually in the Entrypoint.
