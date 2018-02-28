#!/bin/sh

set -e

# Copy the data directory to the mounted volume...
echo "Copying media..."
cp -R data/* /data-loader
# Touch (create) the loaded file to signal that the
# data's present...
echo "Done."
touch /data-loader/loaded
