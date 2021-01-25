Guide
===

***PostgreSQL, Symfony, VueJS***

This guide sources are [available on github](https://github.com/inetum-orleans/ddb-guide-psql-symfony-vue).

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

ddb.Compose({
  services: {
    db: ddb.Image("postgres")
  }
})
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

ddb.Compose({
  services: {
    db: ddb.Image("postgres") +
    {
      environment+: {POSTGRES_PASSWORD: "ddb"}
    }
  }
})
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

```yaml
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

Let's stop and destroy all containers for now.

```bash
docker-compose down
```

Map a named volume to the `db` service inside `docker-compose.yml.jsonnet`.

```json
local ddb = import 'ddb.docker.libjsonnet';

ddb.Compose({
	services: {
		db: ddb.Image("postgres")
		  {
		    environment+: {POSTGRES_PASSWORD: "ddb"},
		    volumes+: ['db-data:/var/lib/postgresql/data']
		  }
    }
})
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

With ddb, you can register those binaries right into `docker-compose.yml.jsonnet` to make them accessible from your local 
environment.

```json
local ddb = import 'ddb.docker.libjsonnet';

ddb.Compose({
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
})

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
    Fixuid change `uid` and `gid` of the container user to match the host user, and it changes files ownerships as 
    declared in `fixuid.yml` configuration file. 
    
    Most of the time, `user` and `group` defined in the configuration file should match the user defined in Dockerfile, 
    and `paths` should match the root directory and volume directories.
    
    When a `fixuid.yml` file is available next to a Dockerfile, ddb generates fixuid installation instructions into the 
    `Dockerfile`, and entrypoint is changed to run fixuid before the default entrypoint.  

Last step, change in `docker-compose.yml.jsonnet` the service definition to use the newly created Dockerfile
(`ddb.Image("postgres")` replaced to `ddb.Build("postgres")`), and set `user` to the host user uid/gid (`ddb.User()`).

```json
local ddb = import 'ddb.docker.libjsonnet';

ddb.Compose({
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
})
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

Setup PHP, Apache and Symfony Skeleton
---

Then, we need to setup PHP FPM with it's related web server Apache.

So, we are creating a new `php` service inside `docker-compose.yml.jsonnet`, based on a Dockerfile build.

```json
local ddb = import 'ddb.docker.libjsonnet';

ddb.Compose({
	services: {
        ...
        php: ddb.Build("php") +
          ddb.User() +
          {
          volumes+: [
            ddb.path.project + ":/var/www/html",
            "php-composer-cache:/composer/cache",
            "php-composer-vendor:/composer/vendor"
          ]
        }
})
```

And the related `Dockerfile.jinja` inside `.docker/php` directory.

```dockerfile
FROM php:7.3-fpm

RUN docker-php-ext-install opcache
RUN yes | pecl install xdebug && docker-php-ext-enable xdebug

RUN apt-get update -y &&\
 apt-get install -y libpq-dev &&\
 rm -rf /var/lib/apt/lists/* &&\
 docker-php-ext-install pdo pdo_pgsql

ENV COMPOSER_HOME /composer
ENV PATH /composer/vendor/bin:$PATH
ENV COMPOSER_ALLOW_SUPERUSER 1

COPY --from=composer:2 /usr/bin/composer /usr/bin/composer
RUN apt-get update -y &&\
 apt-get install -y git zip unzip &&\
 rm -rf /var/lib/apt/lists/*

RUN mkdir -p "$COMPOSER_HOME/cache" \
&& mkdir -p "$COMPOSER_HOME/vendor" \
&& chown -R www-data:www-data $COMPOSER_HOME \
&& chown -R www-data:www-data /var/www

VOLUME /composer/cache
```

And `fixuid.yml` to fix file permission issues.

```yaml
user: www-data
group: www-data
paths:
  - /
  - /composer/cache
```

Then build the docker image with `docker-compose build`.

Composer has been installed in the image, so let's make it available by registering a binary into 
`docker-compose.yml.jsonnet`. We can also register the `php` binary for it to be available locally too.

```jsonnet
local ddb = import 'ddb.docker.libjsonnet';

ddb.Compose({
    services: {
        ...
        php: ddb.Build("php") +
             ddb.User() +
             ddb.Binary("composer", "/var/www/html", "composer") +
             ddb.Binary("php", "/var/www/html", "php") +
             {
              volumes+: [
                 ddb.path.project + ":/var/www/html",
                 "php-composer-cache:/composer/cache",
                 "php-composer-vendor:/composer/vendor"
              ]
             }
        },
})
```

And activate the project, with `$(ddb activate)`. The composer command in now available right in your PATH.

```bash
$ composer --version
Composer version 1.10.10 2020-08-03 11:35:19

$ php --version
PHP 7.3.10 (cli) (built: Oct 17 2019 15:09:28) ( NTS )
Copyright (c) 1997-2018 The PHP Group
Zend Engine v3.3.10, Copyright (c) 1998-2018 Zend Technologies
    with Xdebug v2.9.6, Copyright (c) 2002-2020, by Derick Rethans
```

Now PHP and composer are available, you can generate the symfony skeleton inside a `backend` directory.

```bash
composer create-project symfony/skeleton backend
```

We also need a `web` service for Apache configured with PHP. Here's the `docker-compose.yml.jsonnet` part.

```json
local ddb = import 'ddb.docker.libjsonnet';

local domain_ext = std.extVar("core.domain.ext");
local domain_sub = std.extVar("core.domain.sub");

local domain = std.join('.', [domain_sub, domain_ext]);

ddb.Compose({
	services: {
        ...
        web: ddb.Build("web") +
             ddb.VirtualHost("80", domain)
             {
                  volumes+: [
                     ddb.path.project + ":/var/www/html",
                     ddb.path.project + "/.docker/web/apache.conf:/usr/local/apache2/conf/custom/apache.conf",
                  ]
             },
})
```

!!! note "Use std.extVar(...) inside jsonnet to read a configuration property"
    As you can see here, we are using jsonnet features to build the domain name and setup the traefik configuration for 
    the virtualhost. Configuration properties are available inside all template engines and can be listed with 
    `ddb config --variables`
    
As with the `php` service, a `.docker/web/Dockerfile.jinja` is created to define the image build.

```
FROM httpd:2.4

RUN mkdir -p /usr/local/apache2/conf/custom \
&& mkdir -p /var/www/html \
&& sed -i '/LoadModule proxy_module/s/^#//g' /usr/local/apache2/conf/httpd.conf \
&& sed -i '/LoadModule proxy_fcgi_module/s/^#//g' /usr/local/apache2/conf/httpd.conf \
&& echo >> /usr/local/apache2/conf/httpd.conf && echo 'Include conf/custom/*.conf' >> /usr/local/apache2/conf/httpd.conf

RUN sed -i '/LoadModule headers_module/s/^#//g' /usr/local/apache2/conf/httpd.conf
RUN sed -i '/LoadModule rewrite_module/s/^#//g' /usr/local/apache2/conf/httpd.conf
```

`apache.conf` specified in docker compose volume mount is also generated from a jinja file, `apache.conf.jinja`. It is
 used to inject domain name and docker compose network name, for the domain to be centralized into ddb.yml 
 configuration and ease various environment deployements (stage, prod).

```
<VirtualHost *:80>
  ServerAdmin webmaster@{{core.domain.sub}}.{{core.domain.ext}}
  ServerName api.{{core.domain.sub}}.{{core.domain.ext}}
  DocumentRoot /var/www/html/backend/public

  <Directory "/var/www/html/backend/public/">
    DirectoryIndex index.php

    AllowOverride All
    Order allow,deny
    Allow from all
    Require all granted

    # symfony configuration from https://github.com/symfony/recipes-contrib/blob/master/symfony/apache-pack/1.0/public/.htaccess

    # By default, Apache does not evaluate symbolic links if you did not enable this
    # feature in your server configuration. Uncomment the following line if you
    # install assets as symlinks or if you experience problems related to symlinks
    # when compiling LESS/Sass/CoffeScript assets.
    # Options FollowSymlinks

    # Disabling MultiViews prevents unwanted negotiation, e.g. "/index" should not resolve
    # to the front controller "/index.php" but be rewritten to "/index.php/index".
    <IfModule mod_negotiation.c>
        Options -MultiViews
    </IfModule>

    <IfModule mod_rewrite.c>
        RewriteEngine On

        # Determine the RewriteBase automatically and set it as environment variable.
        # If you are using Apache aliases to do mass virtual hosting or installed the
        # project in a subdirectory, the base path will be prepended to allow proper
        # resolution of the index.php file and to redirect to the correct URI. It will
        # work in environments without path prefix as well, providing a safe, one-size
        # fits all solution. But as you do not need it in this case, you can comment
        # the following 2 lines to eliminate the overhead.
        RewriteCond %{REQUEST_URI}::$1 ^(/.+)/(.*)::\2$
        RewriteRule ^(.*) - [E=BASE:%1]

        # Sets the HTTP_AUTHORIZATION header removed by Apache
        RewriteCond %{HTTP:Authorization} .
        RewriteRule ^ - [E=HTTP_AUTHORIZATION:%{HTTP:Authorization}]

        # Redirect to URI without front controller to prevent duplicate content
        # (with and without `/index.php`). Only do this redirect on the initial
        # rewrite by Apache and not on subsequent cycles. Otherwise we would get an
        # endless redirect loop (request -> rewrite to front controller ->
        # redirect -> request -> ...).
        # So in case you get a "too many redirects" error or you always get redirected
        # to the start page because your Apache does not expose the REDIRECT_STATUS
        # environment variable, you have 2 choices:
        # - disable this feature by commenting the following 2 lines or
        # - use Apache >= 2.3.9 and replace all L flags by END flags and remove the
        #   following RewriteCond (best solution)
        RewriteCond %{ENV:REDIRECT_STATUS} ^$
        RewriteRule ^index\.php(?:/(.*)|$) %{ENV:BASE}/$1 [R=301,L]

        # If the requested filename exists, simply serve it.
        # We only want to let Apache serve files and not directories.
        RewriteCond %{REQUEST_FILENAME} -f
        RewriteRule ^ - [L]

        # Rewrite all other queries to the front controller.
        RewriteRule ^ %{ENV:BASE}/index.php [L]
    </IfModule>

    <IfModule !mod_rewrite.c>
        <IfModule mod_alias.c>
            # When mod_rewrite is not available, we instruct a temporary redirect of
            # the start page to the front controller explicitly so that the website
            # and the generated links can still be used.
            RedirectMatch 307 ^/$ /index.php/
            # RedirectTemp cannot be used instead
        </IfModule>
    </IfModule>
  </Directory>

  SetEnvIf Authorization "(.*)" HTTP_AUTHORIZATION=$1

  <FilesMatch \.php$>
      SetHandler "proxy:fcgi://php.{{docker.compose.network_name}}:9000"
  </FilesMatch>
</VirtualHost>
```

And now, we are ready start all containers : `docker-compose up -d`. 

Run `ddb info` command to check the URL of your virtualhost for the web service.

You should be able to view Symfony landing page at 
[http://ddb-quickstart.test](http://api.ddb-quickstart.test) and 
[https://ddb-quickstart.test](https://api.ddb-quickstart.test).

!!! note "You may have to restart traefik container"
    If you have some issues with certificate validity on the https:// url, you may need to restart traefik container : 
    `docker restart traefik`.
    
Setup VueJS and Vue CLI
---

To be continued