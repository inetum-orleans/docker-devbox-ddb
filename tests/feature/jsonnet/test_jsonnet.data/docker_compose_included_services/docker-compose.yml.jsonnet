local ddb = import 'ddb.docker.libjsonnet';

ddb.Compose({
  services: {
    enabled1: ddb.Image("enabled1"),
    disabled1:  ddb.Image("disabled1"),
    disabled2:  ddb.Image("disabled2")
  }
})
