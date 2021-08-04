local ddb = import 'ddb.docker.libjsonnet';

ddb.Compose({
  services: {
    web: ddb.Build("web")
         + ddb.VirtualHost("80", ddb.subDomain('api'))
         + {
              labels+: {
                  "traefik.http.middlewares.project-dot-com-auth.basicauth.users":"project-dot-com:$$apr1$$oTBtKtGR$$JlgPB1ZdGh1bYfPonp0IB0",
                  ["traefik.http.routers." + ddb.ServiceName() + "-tls.middlewares"]:"project-dot-com-auth"
              },
              volumes: [
                  ddb.path.project + "/.docker/web/nginx.conf:/etc/nginx/conf.d/default.conf:rw",
                  ddb.path.project + ":/var/www/html:rw"
              ]
          }
        }
})
