FROM docker-registry.default:5000/fragalysis-cicd/fragalysis-loader:latest

ENV APP_ROOT /code

# Label the image with the origin of the pre-laoded data.
# Passed to the build process using "--build-arg DATA_ORIGIN=<value>".
ARG DATA_ORIGIN
ENV DATA_ORIGIN ${DATA_ORIGIN}
LABEL data.origin=${DATA_ORIGIN}

COPY docker-entrypoint.sh ${APP_ROOT}/
RUN chmod 755 *.sh && \
    chmod 755 *.py

WORKDIR ${APP_ROOT}
