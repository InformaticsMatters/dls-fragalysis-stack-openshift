#!/bin/sh

set -e

# Copy the media directory to the mounted volume...
echo "Copying media..."
cp -R media/* /code/media
# Touch (create) the loaded file to signal that the
# data's present...
echo "Done."
touch /code/media/loaded
