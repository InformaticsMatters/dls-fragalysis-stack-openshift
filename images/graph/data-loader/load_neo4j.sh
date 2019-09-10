#!/usr/bin/env bash

DATABASE=graph.db

# If the destination database exists (graph.db)
# then leave...
if [ ! -d /data/databases/${DATABASE} ]; then
    echo "(load_neo4j.sh) $(date) Importing into '${DATABASE}'..."
    cd /data-loader
    /var/lib/neo4j/bin/neo4j-admin import \
        --database ${DATABASE} \
        --nodes "nodes-header.csv,nodes.csv" \
        --relationships:FRAG "edges-header.csv,edges.csv" \
        --ignore-duplicate-nodes

    echo "(load_neo4j.sh) $(date) Imported."
    touch loaded
    cd /var/lib/neo4j
    /data-loader/index_neo4j.sh
    echo "(load_neo4j.sh) $(date) Imported."
fi
