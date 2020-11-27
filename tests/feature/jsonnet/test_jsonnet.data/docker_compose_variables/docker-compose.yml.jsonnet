local ddb = import 'ddb.docker.libjsonnet';

local user = "biometrie";
local password = "biometrie";
local certresolver = if ddb.env.is("ci") then "anothercertresolver" else null;
local router_rule = if ddb.env.is("ci") then "HostRegexp(`traefik.io`, `{subdomain:[a-z]+}.traefik.io`, ...)" else null;
local sites = std.extVar('app.sites');

local services = {
    'db' : ddb.Build("db") + ddb.User() + {
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
    }
}

+ {
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
}

+ {
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
}

+ {
    "php": ddb.Build("php") + ddb.User() + ddb.XDebug(version=2) {
        "volumes": [
            "php-composer-cache:/composer/cache:rw",
            "php-composer-vendor:/composer/vendor:rw",
            ddb.path.project + "/.docker/php/conf.d/php-config.ini:/usr/local/etc/php/conf.d/php-config.ini:rw",
            ddb.path.project + ":/var/www/html:rw"
        ]
    },
}

+ {
    "web": ddb.Build("web")
        + ddb.JoinObjectArray([ddb.VirtualHost("80", std.join('.', [site, "biometrie.test"]), site, certresolver=certresolver, router_rule=router_rule) for site in sites])
        + {
            "labels"+: {
                "traefik.http.middlewares.biometrie-auth.basicauth.users":"biometrie:$$apr1$$oTBtKtGR$$JlgPB1ZdGh1bYfPonp0IB0",
                ["traefik.http.routers." + ddb.ServiceName("api") + "-tls.middlewares"]:"biometrie-auth"
            },
            "volumes": [
                ddb.path.project + "/.docker/web/nginx.conf:/etc/nginx/conf.d/default.conf:rw",
                ddb.path.project + ":/var/www/html:rw"
            ]
        }
};
ddb.Compose({ "services": services })
