Djp packages
===

A **djp** package (**d**db **j**sonnet **p**ackage) is a [cookiecutter](./features/cookiecutter.md) template designed to bring docker-compose 
services inside project configuration through [jsonnet docker compose library](./features/jsonnet.md#docker-compose-jsonnet-library). 

Services defined inside a **djp** package are pre-configured to minimize the amount of code to write inside `docker-compose.yml.jsonnet` configuration
file.

Many **djp** packages can be found inside 
[Github Inetum Orléans organisation](https://github.com/inetum-orleans?q=djp-) with repositories starting with `djp-`. 
They are all documented on their own in `README.md` file of each repository.

**djp** packages can be configured and downloaded inside the project with 
[cookiecutter feature](./features/cookiecutter.md) and [download command](./commands.md#ddb-download).

**djp** packages allow reusability among projects and reduce the complexity of your own 
`docker-compose.yml.jsonnet` configuration.

!!! example "Install `inetum-orleans/djp-postgres` djp step by step"

    - Register the template inside [cookiecutter](./features/cookiecutter.md) configuration. `extra_context` property can be used to customize cookiecutter 
    template. Available properties and default values can be found in 
    [cookiecutter.json](https://github.com/inetum-orleans/djp-postgres/blob/main/cookiecutter.json) file inside the 
    repository.

    *ddb.yml*
    ```yaml
    cookiecutter:
      templates:
        - template: gh:inetum-orleans/djp-postgres
          extra_context:
            postgres_version: "13"
    ```

    - Download cookiecutter templates with the ddb command.

    ```bash
    ddb download
    ```

    - Check the djp has been downloaded and configured inside `.docker/postgres`.

    - Import the djp inside `docker-compose.yml.jsonnet` using `ddb.with`function. You can read 
    [README.md]((https://github.com/inetum-orleans/djp-postgres/blob/main/README.md)) of the djp repository to check
    usage. Additional services can still be added manually using jsonnet object composition operator `+`.

    *docker-compose.yml.jsonnet*
    
    ```json
    local ddb = import 'ddb.docker.libjsonnet';
    
    ddb.Compose(
        ddb.with(import '.docker/postgres/djp.libjsonnet', name='db') +
        { services+: {
            sonarqube: ddb.Image("sonarqube:community")
                + ddb.VirtualHost("9000", ddb.domain, "sonarqube")
                + {
                    environment: {
                      'SONAR_ES_BOOTSTRAP_CHECKS_DISABLE': 'true',
                      'SONAR_JDBC_URL': 'jdbc:postgresql://db:5432/' + ddb.projectName,
                      'SONAR_JDBC_USERNAME': ddb.projectName,
                      'SONAR_JDBC_PASSWORD': ddb.projectName
                    },
                    volumes: [
                        "sonarqube-db-data:/var/lib/postgresql/data:rw",
                        "sonarqube_conf:/opt/sonarqube/conf",
                        "sonarqube_data:/opt/sonarqube/data",
                        "sonarqube_extensions:/opt/sonarqube/extensions",
                        "sonarqube_bundled-plugins:/opt/sonarqube/lib/bundled-plugins",
                        ddb.path.project + "/.docker/sonarqube/sonar.properties:/opt/sonarqube/conf/sonar.properties",
                        ddb.path.project + "/plugins/sonarqube-community-branch-plugin.jar:/opt/sonarqube/extensions/plugins/sonarqube-community-branch-plugin.jar",
                        ddb.path.project + "/plugins/sonarqube-community-branch-plugin.jar:/opt/sonarqube/lib/common/sonarqube-community-branch-plugin.jar",
                        ddb.path.project + "/plugins/sonar-dependency-check-plugin.jar:/opt/sonarqube/extensions/plugins/sonar-dependency-check-plugin.jar",
                        ddb.path.project + "/plugins/sonar-auth-oidc-plugin.jar:/opt/sonarqube/extensions/plugins/sonar-auth-oidc-plugin.jar"
                    ]
                }
            }
        }
    )
    ```

!!! example "Advanced `docker-compose.yml.jsonnet` using djp packages / ddb.with() usage"

    `ddb.with()` accepts some optional arguments:

    - `name`: Name of the service
    - `params`: Parameters of the service
    - `append`: Additional configuration to add
    - `when`: Condition to add the service
    
    ```jsonnet
    local ddb = import 'ddb.docker.libjsonnet';
    
    ddb.Compose(
        ddb.with(import '.docker/postgres/djp.libjsonnet',
        name='db',
        params={database: 'estamp'},
        append={
            volumes+: [
                ddb.path.project + "/.docker/postgres/data.sql:/docker-entrypoint-initdb.d/11-data.sql",
                ddb.path.project + "/.docker/postgres/data.fix-jpa-datatypes.sql:/docker-entrypoint-initdb.d/21-data.fix-jpa-datatypes.sql"
            ]
        }) +
    
        ddb.with(import '.docker/mailcatcher/djp.libjsonnet',
        when=!ddb.env.is('prod')) +
    
        ddb.with(import '.docker/openjdk/djp.libjsonnet') +
    
        ddb.with(import '.docker/maven/djp.libjsonnet') +
    
        ddb.with(import '.docker/apache/djp.libjsonnet',
        name='web',
        params={domain: domain}) +
    
        ddb.with(import '.docker/openjdk/djp.libjsonnet',
        name='api',
        append=ddb.VirtualHost("8080", std.join('.', ["api", domain]), "api") + {
            tty: false,
            environment+: [
             "SPRING_PROFILES_ACTIVE=" + std.extVar("core.env.current")
            ],
            working_dir: "/project/runtime",
            entrypoint: "java",
            command: "-jar ../target/estamp-1.0-SNAPSHOT.jar",
        })
    )
    ```

!!! info "Content of a `djp` package"

    A `djp` package contains a `djp.libjsonnet` file that exports a jsonnet object. Rest of the 
    package content are files that should be available in the docker context or used by docker-compose 
    generated configuration.

    The jsonnet object should match the following structure:
    
    | Property | Description |
    | :---------: | :----------- |
    | `factory(name, params={})` | Function called by `ddb.with` that returns a part of docker compose configuration using given service `name` and `params`. Available parameters are documented in README.md file of the djp git repository. |
    | `defaultName` | Default name generated by `ddb.with` function. Should match the cookiecuttter directory. |

!!! info "Publish a `djp` package"

    Your can publish a `djp` package by creating a new public github repository named with `djp-*` from 
    [inetum-orleans/djp-template](https://github.com/inetum-orleans/djp-template/generate) template. This is a github 
    template that contains a basic structure common to any `djp` package.

    After creating the repository, you should follow those steps to make sure the djp will be usable.

    - In `README.md`, customize the title djp-template, Description section, Snippet section and Parameters section. 
    Usage section should be left untouched.

    - In `cookiecutter.json`, add the settings allong with default values of the djp. Those settings are then available
    at download time inside `cookiecutter.templates.extra_context` property 
    (see [cookiecutter](../features/cookiecutter.md) Feature).

    - Everything is processed as a template inside cookiecutter. You can reference properties defined in 
    `cookiecutter.json` using `{{ cookiecutter.<property> }}` Jinja2 syntax.