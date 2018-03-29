#!/usr/bin/env bash

# Assumes the Application's Persistent Volumes are available
# and a number of other container images have been deployed
# (namely the informatics matters images for the data loaders
# and forked repos).

# You will need to define the following environment variables: -
#
#   -   OS_ADMIN_PASSWORD
#   -   OS_DEVELOPER_PASSWORD

# Service account
SA=diamond
# User
OS_DEVELOPER_USER=developer

# It is assumed that the PVs NFS volumes
# have been made available to the OpenShift cluster.

echo
echo "+ Creating PVs..."

oc login -u admin -p $OS_ADMIN_PASSWORD > /dev/null
oc process -f fs-pv-nfs.yaml | oc create -f -

echo
echo "+ Creating PVCs..."

oc login -u $OS_DEVELOPER_USER -p $OS_DEVELOPER_PASSWORD > /dev/null
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
