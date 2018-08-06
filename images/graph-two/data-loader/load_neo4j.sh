#!/usr/bin/env bash

DATABASE=graph.db

# If the destination database exists (graph.db)
# then leave...
if [ ! -d /data/databases/${DATABASE} ]; then
    echo "(load_neo4j.sh) Decompressing graph files..."
    cd /data-loader
    gzip -d *.gz
    echo "(load_neo4j.sh) Importing into '${DATABASE}'..."
    /var/lib/neo4j/bin/neo4j-admin import \
        --database ${DATABASE} \
        --nodes "nodes-header.csv,nodes.csv" \
        --relationships:F2EDGE "edges-header.csv,edges.csv" \
        --ignore-duplicate-nodes

    echo "(load_neo4j.sh) Indexing..."
    touch loaded
    cd /var/lib/neo4j
    /data-loader/index_neo4j.sh
    echo "(load_neo4j.sh) Done."
fi
