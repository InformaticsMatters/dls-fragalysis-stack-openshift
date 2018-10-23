# The Graph DB Dockerfile.
FROM neo4j:3.3.3

ENV NEO4J_EDITION=community
ENV PATH /var/lib/neo4j/bin:$PATH

# Label the image with the origin of the pre-loaded data.
# Passed to the build process using "--build-arg DATA_ORIGIN=<value>".
ARG DATA_ORIGIN
LABEL data.origin=${DATA_ORIGIN}

# Copy source data in (to be used to load the DB).
# This is the content of the data-loader directory.
COPY data-loader/ /data-loader/
RUN chmod 755 /data-loader/index_neo4j.sh
