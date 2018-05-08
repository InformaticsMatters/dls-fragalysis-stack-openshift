#!/usr/bin/env bash

DATABASE=graph.db

# If the destination database exists (graph.db)
# then leave...
if [ ! -d /data/databases/${DATABASE} ]; then

    echo "Importing into '${DATABASE}'..."
    cd /data-loader
    /var/lib/neo4j/bin/neo4j-admin import \
        --database ${DATABASE} \
        --nodes "nodes-header.csv,nodes.csv" \
        --relationships:F2EDGE "edges-header.csv,edges.csv"

    echo "Done."
    cd /var/lib/neo4j

fi
