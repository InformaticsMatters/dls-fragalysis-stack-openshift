#!/usr/bin/env bash

# We expect data to be available at the mount-point
# '/fragalysis' and written to the mount point '/code/media'.
#
# The environment variable 'DATA_ORIGIN' identifies the
# fragalysis directory to be copied, i.e.
# '/fragalysis/django_data/${DATA_ORIGIN}' is written to '/code/media/NEW_DATA'.

# Does the container look intact?
# We need an environment variable and
# a source and destination directory...
if [ -z "${DATA_ORIGIN}" ]; then
    echo "ERROR - the environment variable (DATA_ORIGIN) is not set"
    exit 0
fi
SRC=/fragalysis/django_data/${DATA_ORIGIN}
if [ ! -d "$SRC" ]; then
    echo "ERROR - the source directory ($SRC) does not exist"
    exit 0
fi
if [ ! -d "/code/media" ]; then
    echo "ERROR - the destination directory (/code/media) does not exist"
    exit 0
fi

# OK if we get here...
#
# - Wipe the (temporary) destination directory
# - Copy new content
# - Run the loader
DST=/code/media/NEW_DATA
echo "+> Removing ${DST}"
rm -rf ${DST}
mkdir ${DST}
echo "+> Copying ${DATA_ORIGIN} to ${DST}..."
cp -r ${SRC}/* ${DST}
echo "+> Running loader..."
./run_loader.sh
touch /code/media/loaded
echo "+> Done."
