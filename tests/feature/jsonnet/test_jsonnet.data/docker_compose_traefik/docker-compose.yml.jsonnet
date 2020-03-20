local registryName = std.extVar("docker.registry.name");
local registryRepository = std.extVar("docker.registry.repository");
local restartPolicy = std.extVar("docker.restart_policy");
local projectName = std.extVar("core.project.name");

local BuildService(name, image_name=name) = {
    "build": {
        "cache_from": [
            registryName + registryRepository + image_name
        ],
        "context": "/home/toilal/projects/GLI-APIBiometrie/.docker/" + image_name
    },
	"image": registryName + registryRepository + image_name,
    "init": true,
    "restart": restartPolicy,
};

local ImageService(name, image_name=name) = {
	"image": image_name,
    "init": true,
    "restart": restartPolicy,
};

local TraefikLabels(port, hostname, name=null) = {
    "traefik.enable": "true",
    ["traefik.http.routers." + std.join("-", std.prune([projectName, name])) + "-tls.rule"]: "Host(`" + hostname + "`)",
    ["traefik.http.routers." + std.join("-", std.prune([projectName, name])) + "-tls.service"]: std.join("-", std.prune([projectName, name])),
    ["traefik.http.routers." + std.join("-", std.prune([projectName, name])) + "-tls.tls"]: "true",
    ["traefik.http.routers." + std.join("-", std.prune([projectName, name])) + ".rule"]: "Host(`" + hostname + "`)",
    ["traefik.http.routers." + std.join("-", std.prune([projectName, name])) + ".service"]: std.join("-", std.prune([projectName, name])),
    ["traefik.http.services." + std.join("-", std.prune([projectName, name])) + ".loadbalancer.server.port"]: port
};

local TraefikService(port, hostname, name=null) = {
    "labels": TraefikLabels(port, hostname, name),
    "networks": {
        "default": {},
        "reverse-proxy": {}
    }
};

local user = "biometrie";
local password = "biometrie";

local main = {
	"version": "3.7",
	"services": {
		"db": BuildService("db") {
			"environment": {
				"POSTGRES_PASSWORD": password,
				"POSTGRES_USER": user
			},
			"ports": [
				{
					"published": 16032,
					"target": 5432
				}
			],
			"user": "1000:1000",
			"volumes": [
				"db-data:/var/lib/postgresql/data:rw",
				"/home/toilal/projects/GLI-APIBiometrie:/workdir:rw"
			]
		},
		"db-test": BuildService("db-test", "db") {
			"environment": {
				"POSTGRES_PASSWORD": password,
				"POSTGRES_USER": user
			},
			"ports": [
				{
					"published": 16033,
					"target": 5432
				}
			],
			"user": "1000:1000",
			"volumes": [
				"db-test-data:/var/lib/postgresql/data:rw",
				"/home/toilal/projects/GLI-APIBiometrie:/workdir:rw"
			]
		},
		"keycloak": ImageService("jboss/keycloak:8.0.1") + TraefikService("8080", "keycloak.biometrie.test", "keycloak") {
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
				"/home/toilal/projects/GLI-APIBiometrie/keycloak:/opt/jboss/keycloak/keycloak:rw"
			]
		},
		"keycloak-db": BuildService("keycloak-db") {
			"environment": {
				"POSTGRES_DB": "biometrie",
				"POSTGRES_PASSWORD": password,
				"POSTGRES_USER": user
			},
			"ports": [
				{
					"published": 16042,
					"target": 5432
				}
			],
			"volumes": [
				"/home/toilal/projects/GLI-APIBiometrie/keycloak/init.sql:/docker-entrypoint-initdb.d/init.sql:rw",
				"keycloak-db-data:/var/lib/postgresql/data:rw",
				"/home/toilal/projects/GLI-APIBiometrie:/workdir:rw"
			]
		},
		"ldap": BuildService("ldap") {
			"command": "--copy-service --loglevel debug",
			"environment": {
				"LDAP_ADMIN_PASSWORD": password,
				"LDAP_DOMAIN": "biometrie.test",
				"LDAP_ORGANISATION": "biometrie"
			},
			"ports": [
				{
					"published": 16089,
					"target": 389
				},
				{
					"published": 16036,
					"target": 636
				}
			],
		},
		"node": BuildService("node") + TraefikService("8080", "biometrie.test") {
			"user": "1000:1000",
			"volumes": [
				"/home/toilal/projects/GLI-APIBiometrie:/app:rw",
				"node-cache:/home/node/.cache:rw",
				"node-npm-packages:/home/node/.npm-packages:rw"
			]
		},
		"php": BuildService("php") {
			"environment": {
				"PHP_IDE_CONFIG": "serverName=biometrie",
				"XDEBUG_CONFIG": "remote_enable=on remote_autostart=off idekey=biometrie remote_host=172.17.0.1"
			},
			"user": "1000:1000",
			"volumes": [
				"php-composer-cache:/composer/cache:rw",
				"php-composer-vendor:/composer/vendor:rw",
				"/home/toilal/projects/GLI-APIBiometrie/.docker/php/conf.d/php-config.ini:/usr/local/etc/php/conf.d/php-config.ini:rw",
				"/home/toilal/projects/GLI-APIBiometrie:/var/www/html:rw"
			]
		},
		"web": BuildService("web") + TraefikService("80", "api.biometrie.test", "api") {
			"volumes": [
				"/home/toilal/projects/GLI-APIBiometrie/.docker/web/nginx.conf:/etc/nginx/conf.d/default.conf:rw",
				"/home/toilal/projects/GLI-APIBiometrie:/var/www/html:rw"
			]
		}
	},
	"networks": {
		"reverse-proxy": {
			"external": true,
			"name": "reverse-proxy"
		}
	},
	"volumes": {
		"db-data": {},
		"db-test-data": {},
		"keycloak-db-data": {},
		"node-cache": {},
		"node-npm-packages": {},
		"php-composer-cache": {},
		"php-composer-vendor": {}
	}
};

main
# TODO: Add networks and volumes generation