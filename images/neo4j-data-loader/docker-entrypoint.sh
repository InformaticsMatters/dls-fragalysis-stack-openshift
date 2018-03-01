#!/bin/sh

set -e

# Copy the data directory to the mounted volume...
# And set typical execute permissions.
echo "Copying media..."
cp -R data/* /data-loader
chmod +x /data-loader/*.sh
# Touch (create) the loaded file to signal that the
# data's present...
echo "Done."
touch /data-loader/loaded
