FROM neo4j:3.4.9

ENV NEO4J_EDITION=community
ENV PATH /var/lib/neo4j/bin:$PATH

COPY docker-entrypoint.sh /
RUN chmod 755 /docker-entrypoint.sh
