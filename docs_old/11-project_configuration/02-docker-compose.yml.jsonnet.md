docker-compose.yml.jsonnet
===

docker-devbox-ddb aim to provide an automation of docker-compose and functions related to the execution of your project.

You can : 
1. Create a docker-compose.yml manualy, which will not be dynamic depending of your ddb configuration
2. Create a docker-compose.yml.jsonnet, which will be dynamic using ddb configuration and profide a handfull of automations

If you choose the second options, you will need to use the [Jsonnet syntax](https://jsonnet.org/)

If you want more details on functions provided by ddb, you can check the [lib](../ddb/feature/jsonnet/lib) folder of the jsonnet feature

Once you have created the file, you need to run the following command to generate the docker-compose : 
```
ddb configure
```

If you are working on a template file such as the docker-compose.yml.jsonnet, you can even use the watch option as following :
```
ddb --watch configure
```
This command will auto-recompile the templates file each time you update one 

Futhermore, if the gitignore feature is enabled, files generated from template will automaticaly be added to the .gitignore

This is also applicable to other type of files you want to dynamically generate using jsonnet template engine

# Example
```jsonnet
// This is required in order to benefit from ddb automation
local ddb = import 'ddb.docker.libjsonnet';

// You can define local variables
local db_user = "your-db-user";
local db_password = "your-db-user";

local php_workdir = "/var/www/html";
local node_workdir = "/app";
local mysql_workdir = "/app";

// You can retrieve ddb configuration
local domain = std.join('.', [std.extVar("core.domain.sub"), std.extVar("core.domain.ext")]);
local port_prefix = std.extVar("docker.port_prefix");

// You can define you own functions that you can use in the docker-compose generation
local compile_command(name, args, workdir)= {
    ["ddb.emit.docker:binary[" + name + "](name)"]: name,
    ["ddb.emit.docker:binary[" + name + "](args)"]: args,
    ["ddb.emit.docker:binary[" + name + "](workdir)"]: workdir,
 };

local prefix_port(port, output_port = null)= [port_prefix + (if output_port == null then std.substr(port, std.length(port) - 2, 2) else output_port) + ":" + port];

// Here is the docker-compose definition
ddb.Compose() {
	"services": {
        // ddb.Build will read the "db" folder in ".docker" folder of your project
        // ddb.User will add the user block for the service
		"db": ddb.Build("db") + ddb.User() + {
            // You can define usual docker-compose data if you need to, using variables, function or static values
			"environment": {
                "MYSQL_ROOT_PASSWORD": db_password,
                "MYSQL_DATABASE": db_user,
                "MYSQL_USER": db_user,
                "MYSQL_PASSWORD": db_password,
			},
            // You can set configurations depending on environment variables such as the current environment (dev)
			[if ddb.env.is("dev") then "ports"]: prefix_port("3306"),
			"volumes": [
				"db-data:/var/lib/mysql:rw",
				ddb.path.project + ":" + mysql_workdir
			],
            // And you can add commands which will be converted to binaries and allow you to execute them directly in your commandline
             labels+:
                compile_command("mysql", "mysql  -hdb -u" + db_user + " -p" + db_password, mysql_workdir)
		},
		[if ddb.env.is("dev") then "mail"]: ddb.Build("mail") + ddb.VirtualHost("80", std.join(".", ["mail", domain]), "mail", certresolver=if ddb.env.is("prod") then "letsencrypt" else null) ,
		"node": ddb.Build("node") + ddb.User() + ddb.VirtualHost("8080", std.join(".", ["node", domain]), "node", certresolver=if ddb.env.is("prod") then "letsencrypt" else null) {
			"volumes": [
				ddb.path.project + ":" + node_workdir + ":rw",
				"node-cache:/home/node/.cache:rw",
				"node-npm-packages:/home/node/.npm-packages:rw"
			],
             labels+:
                compile_command("node", "node", node_workdir) +
                compile_command("yarn", "yarn", node_workdir) +
                compile_command("vue", "vue", node_workdir)
		},
        "keycloak-db": ddb.Build("keycloak-db") + ddb.User() + {
            [if ddb.env.is("dev") then "ports"]+: [pp + "42:5432"],
            environment+: {
                "POSTGRES_USER": "keycloak",
                "POSTGRES_PASSWORD": "keycloak"
            },
            volumes+: [
                ddb.path.project + '/keycloak/keycloak.sql:/docker-entrypoint-initdb.d/init-data.sql',
                ddb.path.project + ':/workdir',
                'keycloak-db-data:/var/lib/postgresql/data'
            ]
        },
        // ddb.Image will directly use the image from the registry without using the content of .docker folder
        // ddb.VirtualHost will generate docker-compose configuration to allow the container to be access via url
        keycloak: ddb.Image("jboss/keycloak:8.0.1") + ddb.VirtualHost("8080", "keycloak." + domain, "keycloak") + {
            [if ddb.env.is("dev") then "ports"]+: [pp + "85:8080"],
            environment+: [
              'KEYCLOAK_USER=admin',
              'KEYCLOAK_PASSWORD=admin',
              'PROXY_ADDRESS_FORWARDING=true',
              'DB_VENDOR=postgres',
              'DB_ADDR=keycloak-db',
              'DB_DATABASE=keycloak',
              'DB_USER=keycloak',
              'DB_PASSWORD=keycloak'
            ],
            volumes+: [
                ddb.path.project + '/keycloak/keycloak.sql:/docker-entrypoint-initdb.d/init-data.sql',
                ddb.path.project + ':/workdir',
                'keycloak-db:/var/lib/postgresql/data'
            ],
            depends_on+: ['keycloak-db'],
            links+: ['keycloak-db:postgres']
        },
		"php": ddb.Build("php") + ddb.User() + ddb.XDebug() {
			"volumes": [
				"php-composer-cache:/composer/cache:rw",
				"php-composer-vendor:/composer/vendor:rw",
				ddb.path.project + ":" + php_workdir + ":rw"
			],
            labels+:
                compile_command("php", "php", php_workdir) +
                compile_command("composer", "composer", php_workdir)
		},
		"web": ddb.Build("web") + ddb.VirtualHost("80", domain, "app", certresolver=if ddb.env.is("prod") then "letsencrypt" else null) {
			"volumes": [
				ddb.path.project + "/.docker/web/nginx.conf:/etc/nginx/conf.d/default.conf:rw",
				ddb.path.project + ":/var/www/html:rw"
			]
		}
	}
}
``` 