local ddb = import 'ddb.docker.libjsonnet';

local pp = std.extVar("docker.port_prefix");

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
    }
})