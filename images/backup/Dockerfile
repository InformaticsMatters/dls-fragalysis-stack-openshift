FROM python:3.6.5-alpine3.7

ENV APP_ROOT /bandr
WORKDIR ${APP_ROOT}

# Install the postgres client
RUN apk --update add postgresql-client && \
    apk add --no-cache tzdata && \
    rm -rf /var/cache/apk/*
# Set the Alpine image timezone...
ENV TZ=UTC

# Populate the image...
COPY backup.py ${APP_ROOT}/
RUN chmod 755 ${APP_ROOT}/backup.py

CMD [ "./backup.py" ]
