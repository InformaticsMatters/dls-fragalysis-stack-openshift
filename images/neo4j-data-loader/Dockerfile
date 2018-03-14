# The FragAlysis-Stack Neo4J Data Loader.
# Copies data files to the app's data volume,
FROM alpine:3.7

# Base directory for the application
# Also used for user directory
ENV APP_ROOT /home/loader
ENV PUID 6000
ENV PGID 6000

# Containers should NOT run as root
# (as good practice)
RUN addgroup -g ${PGID} loader && \
    adduser -D -u ${PUID} -G loader loader

COPY data/data.tar.gz ${APP_ROOT}/
COPY docker-entrypoint.sh ${APP_ROOT}/

RUN chmod 777 ${APP_ROOT}/*

WORKDIR ${APP_ROOT}
CMD ["./docker-entrypoint.sh"]
