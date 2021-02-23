Jinja
===

[Jinja](https://jinja.palletsprojects.com/) is template library included in `ddb`. It is used to generate files
using ddb configuration.

!!! summary "Feature configuration (prefixed with `jinja.`)"
    === "Simple"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `disabled` | boolean<br>`false` | Should this feature be disabled ? |
        | `suffixes` | string[]<br>`['.jinja']` | A list of filename suffix to include. |
        | `extensions` | string[]<br>`['.*', '']` | A list of glob of supported extension. |
        | `excludes` | string[]<br>`[]` | A list of glob of filepath to exclude. |
        | `options` | dict[string, object] | Additional options to pass to [Jinja Environment](https://jinja.palletsprojects.com/en/2.11.x/api/#jinja2.Environment). |

    === "Advanced"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `includes` | string[]<br>`['*.jinja{.*,}']` | A list of glob of filepath to include. It is automatically generated from `suffixes` and `extensions`. |

Jinja template processing
--- 

When running the `ddb configuration` command, ddb will look for files matching the list of `includes` configuration and 
not in the `excludes` list.

For each file, it will be processed into his final form. 

In those templates, you can retrieve ddb configuration values simply using the full name of the variable.

!!! question "But ... how do I retrieve the full name of a variable ?"
    Well, as you might already know, you can execute `ddb config` in order to check the configuration used in ddb.
    
    But if you append `--variables` to this command, you will have the variable name to include in your template !

!!! example "dotenv `.env` configuration file generation"
    You want to generate a `.env` file based on your current ddb configuration.
    
    You can create a `.env.jinja` and replace the parts you need to fill with those variables:

    ```bash
    APP_ENV=dev
    APP_SECRET=4271e37e11180de028f11a132b453fb6
    CORS_ALLOW_ORIGIN=^https?://{{core.domain.sub}}\.{{core.domain.ext}}$
    DATABASE_URL=mysql://ddb:ddb@db:3306/ddb
    MAILER_URL=smtp://mail
    ```
    
    As you can see, we have configured `CORS_ALLOW_ORIGIN` using ddb configuration variables.

    Now, we can run `ddb configure`. After the file have been processed, `.env` file is generated next to `.env.jinja` 
    template file.
    
    With `core.domain.sub` set to `ddb` and `core.domain.ext` set to 'test', you will get the following content :

    ```bash
    APP_ENV=dev
    APP_SECRET=4271e37e11180de028f11a132b453fb6
    CORS_ALLOW_ORIGIN=^https?://ddb\.test$
    DATABASE_URL=mysql://ddb:ddb@db:3306/ddb
    MAILER_URL=smtp://mail
    ```
    
    This way, you don't need to manually update `.env` file manually and can keep the whole project configuration 
    centralized.