#!/bin/bash

set -e

# To build the local development code,
# creating various container images: -
#
# Fragalysis 'backend' image
# Fragalysis 'loader' image
# Fragalysis 'stack' image
# The production 'loader'
# The test 'graph'

pushd fragalysis-backend || exit
docker build . -t xchem/fragalysis-backend:latest
popd || exit

pushd fragalysis-loader || exit
docker build . -t xchem/fragalysis-loader:latest
popd || exit

pushd fragalysis-stack || exit
docker build . -t xchem/fragalysis-stack:latest
popd || exit

pushd dls-fragalysis-stack-openshift/images/loader || exit
docker build . -f Dockerfile-local -t xchem/loader:latest
popd || exit

pushd dls-fragalysis-stack-openshift/images/graph || exit
docker build . -t xchem/graph:latest
popd || exit
