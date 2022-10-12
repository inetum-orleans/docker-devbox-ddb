local ddb = import 'ddb.docker.libjsonnet';

ddb.Compose({
	services: {
		db_a: ddb.Image("postgres") + ddb.Expose(5433),
		db_b: ddb.Image("postgres") + ddb.Expose(5432),
		db_c: ddb.Image("postgres") + ddb.Expose(5432),
		db_d: ddb.Image("postgres") + ddb.Expose(5431),
		db_e: ddb.Image("postgres") + ddb.Expose(5438),
		db_f: ddb.Image("postgres") + ddb.Expose(5433),
		db_g: ddb.Image("postgres") + ddb.Expose(5432, protocol="udp"),
		db_h: ddb.Image("postgres") + ddb.Expose(5432, protocol="udp"),
		db_i: ddb.Image("postgres") + {
			ports: [{published: 2938, target: 5438}]
		},
		db_j: ddb.Image("postgres") + {
			ports: [{published: 2938, target: 5438}]
		},
	}
})