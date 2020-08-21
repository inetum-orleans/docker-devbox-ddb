Jinja
===

[Jinja](https://jinja.palletsprojects.com/) is another template library included in `ddb`. It is used to generate files
using ddb configuration and any condition you might need.


Feature Configuration
---

- `disabled`: Definition of the status of the feature. If set to True, all gitignore automations will be disabled.
    - type: boolean
    - default: False
- `excluded`: A list of file or filename template to exclude from the this feature processing
    - type: array of string
    - default: []
- `extensions`: TODO
    - type: array of string
    - default: ['.*', '']
- `includes`: The list of filename template which will be handled by the feature. If not defined in your project, it will
    be generated using `suffixed` and `extensions` configuration values.
    - type: array of string
    - default: ['*.jinja{.*,}']
- `suffixed`: TODO
    - type: array of string
    - default: ['.jinja']
 
!!! example "Configuration"
    ```yaml
    jinja:
      disabled: false
      extensions:
      - .*
      - ''
      includes:
      - '*.jinja{.*,}'
      suffixes:
      - .jinja
    ```

Jinja template processing
--- 

When running the `ddb configuration` command, ddb will look for files matching the list of `includes` configuration and 
not in the `excluded` list.

For each file, it will be processed into his final form. 

In those templates, you can retrieve ddb configuration values simply using the full name of the variable.

!!! question "But ... how do I retrieve the full name of a variable ?"
    Well, as you might already know, you can execute `ddb config` in order to check the configuration used in ddb.
    
    But if you append `--variables` to this command, you will have the variable name to include in your template !
    
An example : symfony `.env` generation 
--- 
Let us say that you are working on a symfony project, and you want to generate the `.env` file based on your current
ddb configuration.

Well, you need to create a `.env.jinja` for instance, and replace the parts you need to fill with those variable 
as follows :
```dotenv
APP_ENV=dev
APP_SECRET=4271e37e11180de028f11a132b453fb6
CORS_ALLOW_ORIGIN=^https?://{{core.domain.sub}}\.{{core.domain.ext}}$
DATABASE_URL=mysql://ddb:ddb@db:3306/ddb
MAILER_URL=smtp://mail
```

As you can see, we have replaced the full domain of the `CORS_ALLOW_ORIGIN` variable with ddb configurations variables.

Now, we simply execute `ddb configure`. After the file have been processed by the feature, the final `.env` file will
be on your drive, right next to his jinja counterpart. 

With `core.domain.sub` equals to 'ddb' and `core.domain.ext` set to 'ext', you will get the following content :
```dotenv
APP_ENV=dev
APP_SECRET=4271e37e11180de028f11a132b453fb6
CORS_ALLOW_ORIGIN=^https?://ddb\.test$
DATABASE_URL=mysql://ddb:ddb@db:3306/ddb
MAILER_URL=smtp://mail
```

This way, you will not need to manually update your project configuration manually, but you will simply need to execute
the `ddb configure` command !