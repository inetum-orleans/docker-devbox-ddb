local ddb = import 'ddb.docker.libjsonnet';

ddb.Compose({
	services: {
    s1:
      ddb.Image("alpine:3.6") +
      {
        volumes+: ['shared-volume:/share'],
      },
    s2: ddb.Image("alpine:3.6") +
      {
        volumes+: ["another-volume:/another"],
      },
    s3:
      ddb.Image("alpine:3.6") +
      {
        volumes+: ['shared-volume:/share']
      },
    },
})
