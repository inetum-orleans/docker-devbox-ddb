Docker
===

The docker feature brings docker and docker-compose integration. You may also check [Jsonnet Feature](./jsonnet.md), as
using jsonnet docker specific library brings many Docker related features to `ddb`.

!!! summary "Feature configuration (prefixed with `symlinks.`)"
    | Property | Type | Description |
    | :---------: | :----: | :----------- |
    | `disabled` | boolean<br>`false` | Should this feature be disabled ? |
    | `ip` | string | IP Address of the docker engine |
    | `interface` | string | Network interface of the docker engine |
    | `docker_command` | string<br>`docker` | command used to run docker CLI |
    | `docker_compose_command` | string<br>`docker compose` | command used to run docker compose CLI |
    | `user.uid` | string | The user UID to use inside a container when [jsonnet](./jsonnet.md) `User()` function is used. |
    | `user.gid` | string | The user GID to use inside a container when [jsonnet](./jsonnet.md) `User()` function is used. |
    | `user.name` | string | The host username that will get converted to UID to use inside a container when [jsonnet](./jsonnet.md) `User()` function is used. |
    | `user.group` | string | The host groupname that will get converted to GID to use inside a container when [jsonnet](./jsonnet.md) `User()` function is used. |
    | `path_mapping` | Dict[str, str] | Path mappings to apply on declared volume sources. |

docker-compose configuration processing
---

When a `docker-compose.yml` is found or generated from templates, the content is parsed.

All labels prefixed `ddb.emit.` are processed and converted into event and event arguments.

!!! info "Creation of binaries"
    Whether you use `ddb.Binary()` in jsonnet template or manually add labels to `docker-compose.yml`, they 
    are converted into ddb configuration and shims are generated to run the declared binary as simple executable 
    command, thanks to [shell](shell.md) feature.