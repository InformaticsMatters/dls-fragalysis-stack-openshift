FROM xchem/fragalysis-loader:latest

ENV APP_ROOT /code
ENV APP_USER_ID 2000
RUN useradd -c 'Container user' --user-group --uid ${APP_USER_ID} --home-dir ${APP_ROOT} -s /bin/bash frag

# Label the image with the origin of the pre-laoded data.
# Passed to the build process using "--build-arg DATA_ORIGIN=<value>".
ARG DATA_ORIGIN
LABEL data.origin=${DATA_ORIGIN}

# Copy source data in.
# This is the content of the media directory.
COPY media/ /code/media/

# Change ownership of applicaiton root
RUN chown -R 2000.2000 ${APP_ROOT}

RUN chmod 755 ${APP_ROOT}/*.sh
RUN chmod 755 ${APP_ROOT}/*.py
RUN chmod 777 ${APP_ROOT}/media

WORKDIR ${APP_ROOT}
USER 2000
CMD ["./run_loader.sh"]
