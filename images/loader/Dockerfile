FROM docker-registry.default.svc:5000/fragalysis-cicd/fragalysis-loader:latest

ENV APP_ROOT /code

# The image build number.
# This should be different and ideally incrementing for each build.
# It's probably just the Jenkins BUILD_ID.
ARG BUILD_NUMBER
LABEL build.number=${BUILD_NUMBER}

# Label the image with the origin of the selected data.
# Passed to the build process using "--build-arg DATA_ORIGIN=<value>".
ARG DATA_ORIGIN
ENV DATA_ORIGIN ${DATA_ORIGIN}
LABEL data.origin=${DATA_ORIGIN}

COPY docker-entrypoint.sh ${APP_ROOT}/
RUN chmod 755 *.sh && \
    chmod 755 *.py

WORKDIR ${APP_ROOT}

# Echo upstream Git commits
RUN git log --pretty=format:'%h' -n 1
