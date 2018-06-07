 #!/usr/bin/env bash
 
/var/lib/neo4j/bin/neo4j-shell -v -path /data/databases/graph.db -f << EOF
CREATE INDEX ON :F2(smiles);
schema await
EOF
