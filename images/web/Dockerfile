FROM xchem/fragalysis-stack:latest

# Label the image with the origin of the pre-laoded data.
# Passed to the build process using "--build-arg DATA_ORIGIN=<value>".
ARG DATA_ORIGIN
LABEL data.origin=${DATA_ORIGIN}

# Copy source data in.
# This is the content of the media directory.
COPY media/ /code/media/
