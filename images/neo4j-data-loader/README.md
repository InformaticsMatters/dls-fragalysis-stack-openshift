# The Neo4J data-loader image
Copies data files to a mounted volume. Place your data files into
the `data` directory (feel free to use `.tar.gz` to save space
as the build will automatically unpack them) but consider adding the
files to the project's `.gitignore`.

It expects a volume mount at `/data-loader`.

## Building
Build with...

    $ docker build . -t informaticsmatters/neo4j-data-loader:stable
