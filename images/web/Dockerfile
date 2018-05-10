# The Fragalysis image (sans-media).
FROM abradle/fragalysis-stack:latest

# Label the image with the origin of the pre-laoded data.
# Passed to the build process using "--build-arg data_origin=<value>".
ARG DATA_ORIGIN
LABEL data.origin=$DATA_ORIGIN

# Copy source data in (to be used to load the DB).
# This is the content of the data-loader directory.
COPY media/ /media/
