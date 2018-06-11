# The Fragalysis image (sans-media).
# Sadly ARG-before-FROM is not supported by buildah 1.0
# otherwise I'd do this...
#  ARG FROM_NAMESPACE=docker-registry.default:5000/fragalysis-cicd
#  FROM ${FROM_NAMEPACE}/fragalysis-stack:latest
FROM docker-registry.default:5000/fragalysis-cicd/fragalysis-stack:latest

# Label the image with the origin of the pre-laoded data.
# Passed to the build process using "--build-arg DATA_ORIGIN=<value>".
ARG DATA_ORIGIN
LABEL data.origin=${DATA_ORIGIN}

# Copy source data in.
# This is the content of the media directory.
COPY media/ /code/media/
