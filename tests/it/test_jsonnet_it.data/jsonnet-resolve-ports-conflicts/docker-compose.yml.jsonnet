local ddb = import 'ddb.docker.libjsonnet';

ddb.Compose({
	services: {
		db1: ddb.Image("postgres") + ddb.Expose("5433"),
		db2: ddb.Image("postgres") + ddb.Expose("5432"),
		db3: ddb.Image("postgres") + ddb.Expose("5432"),
		db4: ddb.Image("postgres") + ddb.Expose("5431"),
		db5: ddb.Image("postgres") + ddb.Expose("5438"),
		db6: ddb.Image("postgres") + ddb.Expose("5433"),
	}
})