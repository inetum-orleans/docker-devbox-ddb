local ddb = import 'ddb.docker.libjsonnet';

local pp = std.extVar("docker.port_prefix");
local domain_ext = std.extVar("core.domain.ext");
local domain_sub = std.extVar("core.domain.sub");

local domain = std.join(".", [domain_sub, domain_ext]);

local elk_version = "7.9.1";

local db = {
  name: std.extVar("app.db.name"),
  username: std.extVar("app.db.username"),
  password: std.extVar("app.db.password")
};

ddb.Compose({
	services: {
	  db: ddb.Build("db") +
          ddb.Binary("psql", "/workdir", "psql --dbname=postgresql://" + db.username + ":" + db.password + "@db/" + db.name) +
          ddb.Binary("pg_dump", "/workdir", "pg_dump --dbname=postgresql://" + db.username + ":" + db.password + "@db/" + db.name) +
          ddb.Binary("pg_restore", "/workdir", "pg_restore") +
	      {
	          [if ddb.env.is("dev") then "ports"]+: [pp + "32:5432"],
            environment+: {
                "POSTGRES_USER": db.username,
                "POSTGRES_PASSWORD": db.password,
            },
            volumes+: [
               ddb.path.project + ":/workdir",
               "db-data:/var/lib/postgresql/data",
            ]
        },
      elastic: ddb.Image("docker.elastic.co/elasticsearch/elasticsearch:" + elk_version) +
               ddb.VirtualHost("9200", std.join(".", ["elastic", domain]), "elastic") +
              {
                [if ddb.env.is("dev") then "ports"]+: [pp + "92:9200"],
                environment+: {
                  "discovery.type": "single-node",
                  "ES_JAVA_OPTS": "-Xms512m -Xmx512m"
                },
                volumes+: [
                   "elastic-data:/usr/share/elasticsearch/data"
                ]
            },
    }
})