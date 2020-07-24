Guide
===

***PostgreSQL, Symfony, VueJS***

This guide sources are [available on github](https://github.com/gfi-centre-ouest/ddb-guide-psql-symfony-vue).

Create empty project directory
---

First of all, you need an empty directory for your project.

```bash
mkdir ddb-guide
cd ddb-guide
```

Setup database
---

You should now setup the database container. Create `docker-compose.yml.jsonnet` file, and add the following content:

```json
local ddb = import 'ddb.docker.libjsonnet';

ddb.Compose() {
	services: {
		db: ddb.Image("postgres")
    }
}
```

!!! note "Jsonet, a data templating language"
    Instead of defining containers right inside `docker-compose.yml` with yaml, ddb is using
    [Jsonnet](https://jsonnet.org/), a data templating language. Inside the jsonnet file, a library is imported to
    bring handy features and consistent behavior for all containers while reducing verbosity.
    
!!! note "Jsonet is embedded into ddb"
    [Jsonnet](https://jsonnet.org/) is embedded into ddb. You only have to use the right file extension for ddb to 
    process it through the appropriate template engine.
    
!!! note "Other template languages are supported"
    ddb embeds other templating languages, like 
    [Jinja](https://jinja.palletsprojects.com/) and [ytt](https://get-ytt.io/). But for building the 
    `docker-compose.yml` file, [Jsonnet](https://jsonnet.org/) is the best choice and brings access to all features 
    from ddb.

Run the ddb `configure` command

```bash
ddb configure
```

!!! note "Commands"
    ddb is a command line tool, and implements many commands. `configure` is the main one. It configures the 
    whole project based on available files in the project directory.

`docker-compose.yml` file has been generated.

```yaml
networks: {}
services:
  db:
    image: postgres
    init: true
    restart: 'no'
version: '3.7'
volumes: {}
```

!!! note ".gitignore automation for generated files"
    You may have noticed that a `.gitignore` has also been generated, to exclude `docker-compose.yml`. ddb may generates
    many files from templates. When ddb generates a file, it will always be added to the `.gitignore` file.

Launch the stack with docker-compose, and check database logs.

```bash
docker-compose up -d
docker-compose logs db
```

Sadly, there's an error in logs and container has stopped. You only have to define a database password with environment 
variable `POSTGRES_PASSWORD`.

Add this environment variable to `docker-compose.yml.jsonnet` template.

```json
local ddb = import 'ddb.docker.libjsonnet';

ddb.Compose() {
	services: {
		db: ddb.Image("postgres")
		  {
		    environment+: {POSTGRES_PASSWORD: "ddb"}
		  }
    }
}
```

!!! note "Jsonnet"
    You may feel uncomfortable at first with [Jsonnet](https://jsonnet.org/), but this is a great tool and it brings a 
    huge value to ddb.
    
    Here, we are merging the json object returned by `ddb.Image("postgres")` with another object containing an  
    `environment` key with environment variable values. 
    
    `+` behind `environment` key name means that values from the new object are appended to values from the source one, 
    instead of beeing replaced.
    
    To fully understand syntax and capabilities of jsonnet, you should [take time to learn it](https://jsonnet.org/learning/tutorial.html).

Run `configure` command again.

```bash
ddb configure
```

The generated `docker-compose.yml` file should now look like this:

```
networks: {}
services:
  db:
    environment:
      POSTGRES_PASSWORD: ddb
    image: postgres
    init: true
    restart: 'no'
version: '3.7'
volumes: {}
```

```bash
docker-compose up -d
docker-compose logs db
```

The database should be up now ! Great :)

Start watch mode
---

As you now understand how ddb basics works, you may feel that running the `ddb configure` after each change is annoying.

I'm pretty sure you want to stay a happy developer, so open a new interpreter, cd inside project directory, and run 
`configure` command with `--watch` flag.

```bash
ddb --watch configure
```

ddb is now running and listening for file events inside the project. 

Try to change database password inside the `docker-compose.yml.jsonnet` template file, it will immediately refresh 
`docker-compose.yml`. That's what we call *Watch mode*.

Add a named volume
---

As you may already know, you need to setup a volume for data to be persisted if the container is destroyed. 

Let's stop all containers for now.

```bash
docker-compose down
```

Map a named volume to the `db` service inside `docker-compose.yml.jsonnet`.

```json
local ddb = import 'ddb.docker.libjsonnet';

ddb.Compose() {
	services: {
		db: ddb.Image("postgres")
		  {
		    environment+: {POSTGRES_PASSWORD: "ddb"},
		    volumes+: ['db-data:/var/lib/postgresql/data']
		  }
    }
}
```

Thanks to watch mode, changes are immediately generated in `docker-compose.yml` file

```yaml
networks: {}
services:
  db:
    environment:
      POSTGRES_PASSWORD: ddb
    image: postgres
    init: true
    restart: 'no'
    volumes:
    - db-data:/var/lib/postgresql/data
version: '3.7'
volumes:
  db-data: {}
```

`db-data` volume is now mapped on `/var/lib/postgresql/data` inside `db` service. And `db-data` volume 
has also been declared in the main volumes section ! Magic :)

!!! note "In fact, it's not so magic"
    Those automated behavior provided by `docker-compose.yml.jsonnet`, like `init` and `restart` on each service, 
    and global `volumes` declaration, are handled by ddb jsonnet library through `ddb.Compose()` function.
    
    For more information, check [Jsonnet Feature](../features/jsonnet.md) section.
    
Register binary from image
---

Database docker image contains binaries that you may need to run, like ...

  - `psql` - PostgreSQL client binary.
  - `pg_dump` - PostgreSQL command line tool to export data to a file.

With docker-compose or raw docker, it may be really painful to find out the right `docker-compose` command to run those 
binary from your local environment. You may also have issues to read input data file, or to write output data file.

With ddb, you can register those binaries a single time inside `docker-compose.yml.jsonnet` to bring them to your local 
environment.

```json
local ddb = import 'ddb.docker.libjsonnet';

ddb.Compose() {
	services: {
		db: ddb.Image("postgres") +
		    ddb.Binary("psql", "/project", "psql --dbname=postgresql://postgres:ddb@db/postgres") +
		    ddb.Binary("pg_dump", "/project", "pg_dump --dbname=postgresql://postgres:ddb@db/postgres") +
		  {
		    environment+: {POSTGRES_PASSWORD: "ddb"},
		    volumes+: [
          'db-data:/var/lib/postgresql/data',
          ddb.path.project + ':/project'
		    ]
		  }
    }
}

```

You should notice that some binary files have been generated in `.bin` directory : `psql` and `pg_dump`.

Those binaries are available right now on your local environment. You can check their version.

```bash
.bin/psql --version
.bin/pg_dump --version
```

!!! question "But ... What the ... Where is all the docker hard stuff ?"
    Of course, the docker hard stuff is still there. But it's hidden. ddb generates some shims for those binaries 
    available in docker image, so you fell like those binaries are now installed on the project. But when invoking those 
    binary shims, it creates a temporary container for the command's lifetime.
    
!!! note "Current working directory is mapped"
    When registering binary from jsonnet this way, the project directory on your local environment should be mounted to 
    `/project` inside the container. The working directory of the container is mapped to the working directory of your 
    local environment. This allow ddb to match working directory from local environment and container, so you are able
    to access any files through a natural process. 

!!! note "Default arguments"
    `--dbname=postgresql://postgres:ddb@db/postgres` is added as a default argument to both command, so the commands won't
    require any connection settings.

To bring `psql` and `pg_dump` shims into the path, you have to activate the project environment into your interpreter.

```bash
$(ddb activate)
```

`.bin` directory is now in the interpreter's `PATH`, so `psql` and `pg_dump` are available anywhere.

```bash
psql --version
pg_dump --version
```

Let's try to perform a dump with `pg_dump`.

```bash
pg_dump -f dump.sql
```

Great, the dump.sql file appears in your working directory ! Perfect. 

But if you check carefully your project directory, there's a problem here ! The dump file has been generated, but it is 
owned by `root`. You are not allowed to write or delete this file now. 

Thanks to `sudo`, you can do still delete it.

```bash
sudo rm dump.sql
```

But this suck ... As a developer, you are really disappointed ... And you are right. Nobody wants a file to be owned by
`root` inside the project directory.

Workaround permission issues
---

To workaround those permission issues, ddb has automated the installation of [fixuid](https://github.com/boxboat/fixuid)
inside a Dockerfile.

!!! note "Docker and permission issues"
    Permission issues are a common pitfall while using docker on development environments. They are related to the way 
    docker works and cannot really be fixed once for all.

As you know, ddb like templates, so you are going to use [Jinja](https://jinja.palletsprojects.com/) for all `Dockerfile` 
files.

By convention, custom `Dockerfile.jinja` lies in `.docker/<image>` directory, where `<image>` is to be replaced 
with effective image name.

First step, create `.docker/postgres/Dockerfile.jinja` from postgres base image.

```dockerfile
FROM postgres
USER postgres
```

Second step, create `.docker/postgres/fixuid.yml` file.

```yaml
user: postgres
group: postgres
paths:
  - /
  - /var/lib/postgresql/data
```

!!! note "Fixuid"
    When installed in the image, entrypoint is changed to run fixuid before the default entrypoint.
     
    Fixuid change uid/gid of the user to match the host user, and chown directories declared in configuration 
    recursively to this user. 
    
    Most of the time, `user` and `group` should match the user defined in Dockerfile, and 
    `paths` should match the root directory and volume directories.

Last step, change in `docker-compose.yml.jsonnet` the service definition to use the newly created Dockerfile
(`ddb.Image("postgres")` replaced to `ddb.Build("postgres")`), and set `user` to the host user uid/gid (`ddb.User()`).

```json
local ddb = import 'ddb.docker.libjsonnet';

ddb.Compose() {
	services: {
		db: ddb.Build("postgres") + ddb.User() +
		    ddb.Binary("psql", "/project", "psql --dbname=postgresql://postgres:ddb@db/postgres") +
		    ddb.Binary("pg_dump", "/project", "pg_dump --dbname=postgresql://postgres:ddb@db/postgres") +
		  {
		    environment+: {POSTGRES_PASSWORD: "ddb"},
		    volumes+: [
          'db-data:/var/lib/postgresql/data',
          ddb.path.project + ':/project'
		    ]
		  }
    }
}
```

Stop containers, destroy data from existing database, and start again.

```bash
docker-compose down -v
docker-compose up -d
```

Perform the dump.

```bash
pg_dump -f dump.sql
```

`dump.sql` is now owned by your own user, and as a developer, you are happy again :)

Setup PHP
---

To be continued ...