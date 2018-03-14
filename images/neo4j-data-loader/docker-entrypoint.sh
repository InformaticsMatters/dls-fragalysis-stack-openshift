#!/bin/sh

set -e

# Copy the data to the mounted volume, unpack
# and set typical execute permissions.
echo "Unpacking media..."
tar xf data.tar.gz -C /data-loader --strip-components=1
chmod +x /data-loader/*.sh
# Touch (create) the loaded file to signal that the
# data's present...
echo "Done."
touch /data-loader/loaded
