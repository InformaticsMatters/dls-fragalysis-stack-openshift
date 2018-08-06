# The Graph DB Dockerfile.
FROM neo4j:3.3.3

ENV NEO4J_EDITION=community
ENV PATH /var/lib/neo4j/bin:$PATH

LABEL data.origin=Jun2018-7

# Copy source data in (to be used to load the DB).
# This is the content of the data-loader directory.
COPY data-loader/ /data-loader/
RUN chmod 755 /data-loader/load_neo4j.sh
RUN chmod 755 /data-loader/index_neo4j.sh
