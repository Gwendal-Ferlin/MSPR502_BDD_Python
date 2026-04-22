FROM mongo:7 AS mongo_tools
FROM rclone/rclone:latest AS rclone_bin

FROM postgres:16 AS backup

# No apt-get: copy tools from official images
COPY --from=mongo_tools /usr/bin/mongodump /usr/bin/mongodump
COPY --from=mongo_tools /usr/bin/mongosh /usr/bin/mongosh
COPY --from=rclone_bin /usr/local/bin/rclone /usr/bin/rclone

WORKDIR /app
COPY run-backup.sh /app/run-backup.sh
RUN chmod +x /app/run-backup.sh

ENTRYPOINT ["/app/run-backup.sh"]
