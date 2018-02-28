# The FragAlysis-Stack Django Media loader.
# Copies media files to the app's media volume,
# anxd expected to run prior to the app.
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

ADD media/media.tar.gz ${APP_ROOT}/
COPY docker-entrypoint.sh ${APP_ROOT}/

RUN chmod 755 ${APP_ROOT}/*.sh
RUN chmod 777 ${APP_ROOT}/media

WORKDIR ${APP_ROOT}
CMD ["./docker-entrypoint.sh"]
