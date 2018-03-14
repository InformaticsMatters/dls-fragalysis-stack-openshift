#!/bin/sh

set -e

# Copy the data to the mounted volume and unpack...
echo "Unpacking media..."
tar xf media.tar.gz -C /code/media --strip-components=1
# Touch (create) the loaded file to signal that the
# data's present...
echo "Done."
touch /code/media/loaded
