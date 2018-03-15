#!/usr/bin/env bash

# Assumes the Application's Persistent Volumes are available.
#
# This deployment also assumes you have a number of other container
# images that (at the time of writing) have not been deployed. Namely: -
#
#   abradle/fragalysis-stack:1.0.0
#   abradle/fragalysis-stack-media-loader:1.0.0
#   abradle/neo4j-data-loader:1.0.0

# Service account
SA=diamond
# User
USER=diamond
PASSWORD=diamond

# It is assumed that the PVs NFS volumes
# have been made available to the OpenShift cluster.

echo
echo "+ Creating PVs..."

oc login -u admin -p $OS_ADMIN_PASSWORD > /dev/null
oc process -f fs-pv-nfs.yaml | oc create -f -

echo
echo "+ Creating PVCs..."

oc login -u $USER -p $PASSWORD > /dev/null
oc project fragalysis-stack > /dev/null

oc process -f ../templates/fs-graph-pvc.yaml | oc create -f -
oc process -f ../templates/fs-db-pvc.yaml | oc create -f -
oc process -f ../templates/fs-cartridge-pvc.yaml | oc create -f -
oc process -f ../templates/fs-web-pvc.yaml | oc create -f -

echo
echo "+ Creating Secrets..."

oc process -f ../templates/fs-secrets.yaml | oc create -f -

echo
echo "+ Deploying Loaders..."

oc process -f ../templates/fs-web-media-loader.yaml | oc create -f -
oc process -f ../templates/fs-graph-data-loader.yaml | oc create -f -

echo
echo "+ Deploying Application..."

oc process -f ../templates/fs-graph.yaml | oc create -f -
oc process -f ../templates/fs-db.yaml | oc create -f -
oc process -f ../templates/fs-cartridge.yaml | oc create -f -
oc process -f ../templates/fs-web.yaml | oc create -f -
