local ddb = import 'ddb.docker.libjsonnet';

local user = "biometrie";
local password = "biometrie";
local certresolver = if ddb.env.is("ci") then "anothercertresolver" else null;
local routers_rule = if ddb.env.is("ci") then "HostRegexp(`traefik.io`, `{subdomain:[a-z]+}.traefik.io`, ...)" else null;

ddb.Compose() {
	"services": {
		"db": ddb.Build("db") + ddb.User() + {
			"environment": {
				"POSTGRES_PASSWORD": password,
				"POSTGRES_USER": user
			},
			[if ddb.env.is("dev") then "ports"]: ["16032:5432"],
			"volumes": [
				"db-data:/var/lib/postgresql/data:rw",
				{
				    "source": ddb.path.project,
				    "target": "/workdir",
				    "type": "bind"
				}
			]
		},
		[if ddb.env.index() >= ddb.env.index("ci") then "db-test"]: ddb.Build("db-test", "db") + ddb.User() {
			"environment": {
				"POSTGRES_PASSWORD": password,
				"POSTGRES_USER": user
			},
			[if ddb.env.is("dev") then "ports"]: ["16033:5432"],
			"volumes": [
				"db-test-data:/var/lib/postgresql/data:rw",
				ddb.path.project + ":/workdir"
			]
		},
		"keycloak":  ddb.Image("jboss/keycloak:8.0.1") + ddb.VirtualHost("8080", "keycloak.biometrie.test", "keycloak", certresolver=certresolver) {
			"command": [
				"-b 0.0.0.0 -Dkeycloak.import=/opt/jboss/keycloak/keycloak/realm-export.json"
			],
			"depends_on": [
				"keycloak-db"
			],
			"environment": {
				"DB_ADDR": "keycloak-db",
				"DB_DATABASE": "biometrie",
				"DB_PASSWORD": password,
				"DB_USER": user,
				"DB_VENDOR": "postgres",
				"KEYCLOAK_PASSWORD": password,
				"KEYCLOAK_USER": user,
				"PROXY_ADDRESS_FORWARDING": "true"
			},
			"links": [
				"keycloak-db:postgres"
			],
			"volumes": [
				ddb.path.project + "/keycloak:/opt/jboss/keycloak/keycloak:rw"
			]
		},
		"keycloak-db": ddb.Build("keycloak-db") {
			"environment": {
				"POSTGRES_DB": "biometrie",
				"POSTGRES_PASSWORD": password,
				"POSTGRES_USER": user
			},
			[if ddb.env.is("dev") then "ports"]: ["16042:5432"],
			"volumes": [
				ddb.path.project + "/keycloak/init.sql:/docker-entrypoint-initdb.d/init.sql:rw",
				"keycloak-db-data:/var/lib/postgresql/data:rw",
				ddb.path.project + ":/workdir:rw"
			]
		},
		[if ddb.env.is("dev") then "ldap"]: ddb.Build("ldap") {
			"command": "--copy-service --loglevel debug",
			"environment": {
				"LDAP_ADMIN_PASSWORD": password,
				"LDAP_DOMAIN": "biometrie.test",
				"LDAP_ORGANISATION": "biometrie"
			},
			[if ddb.env.is("dev") then "ports"]: [
			    "16089:389",
			    "16036:636"
			],
		},
		"node": ddb.Build("node") + ddb.User()
		    + ddb.VirtualHost("8080", "biometrie.test", certresolver=certresolver)
		    + (if ddb.env.is("dev") then ddb.VirtualHost("3000", "gulp.biometrie.test", "gulp") else {})
		    {
			"volumes": [
				ddb.path.project + ":/app:rw",
				"node-cache:/home/node/.cache:rw",
				"node-npm-packages:/home/node/.npm-packages:rw"
			]
		},
		"php": ddb.Build("php") + ddb.User() + ddb.XDebug() {
			"volumes": [
				"php-composer-cache:/composer/cache:rw",
				"php-composer-vendor:/composer/vendor:rw",
				ddb.path.project + "/.docker/php/conf.d/php-config.ini:/usr/local/etc/php/conf.d/php-config.ini:rw",
				ddb.path.project + ":/var/www/html:rw"
			]
		},
		"web": ddb.Build("web") + ddb.VirtualHost("80", "api.biometrie.test", "api", certresolver=certresolver, routers_rule=routers_rule) {
			"volumes": [
				ddb.path.project + "/.docker/web/nginx.conf:/etc/nginx/conf.d/default.conf:rw",
				ddb.path.project + ":/var/www/html:rw"
			]
		}
	}
}
