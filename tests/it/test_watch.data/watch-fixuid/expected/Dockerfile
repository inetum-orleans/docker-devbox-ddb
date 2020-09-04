FROM alpine:3.12

# Mount this volume to help loading/exporting dumps
RUN mkdir /workdir
VOLUME /workdir

ADD fixuid.tar.gz /usr/local/bin
RUN chown root:root /usr/local/bin/fixuid && chmod 4755 /usr/local/bin/fixuid && mkdir -p /etc/fixuid
COPY fixuid.yml /etc/fixuid/config.yml
USER mysql

CMD ["--character-set-server=utf8mb4", "--collation-server=utf8mb4_unicode_ci"]
ENTRYPOINT ["fixuid", "-q", "mysql"]
