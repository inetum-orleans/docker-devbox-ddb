local ddb = import 'ddb.docker.libjsonnet';

ddb.Compose({
	services: {
    s1:
      ddb.Image("alpine:3.6") +
      ddb.Expose(21) +
      ddb.Expose(22, null, "udp") +
      ddb.Expose(23, 99, "tcp") +
      {
        ports+: ["9912:9912"]
      }
    }
})
