#!/usr/bin/env bash

# Assumes the Application's Persistent Volumes are available
# and a number of other container images have been deployed
# (namely the informatics matters images for the data loaders
# and forked repos).
#
# Here I also assumed that the project (fragalysis-stack) also exists.
#
# It is assumed that the PVs NFS volumes
# have been made available to the OpenShift cluster.

# You will need to be logged into the cluster (master).
# The master is exposed on 130.246.215.45: -
#
#   oc login 130.246.215.45 -u admin

# You will need to have logged in as the admin user at some point in the past.

echo
echo "+ Creating PVs..."

oc login -u admin > /dev/null
oc process -f fs-pv-nfs.yaml | oc create -f -

echo
echo "+ Creating PVCs..."

oc project fragalysis-cicd > /dev/null

oc process -f ../templates/fs-db-pvc.yaml | oc create -f -
oc process -f ../templates/fs-cartridge-pvc.yaml | oc create -f -

echo
echo "+ Creating Secrets..."

oc process -f ../templates/fs-secrets.yaml | oc create -f -

echo
echo "+ Deploying Application..."

oc process -f ../templates/fs-graph.yaml | oc create -f -
oc process -f ../templates/fs-db.yaml | oc create -f -
oc process -f ../templates/fs-cartridge.yaml | oc create -f -
oc process -f ../templates/fs-web.yaml | oc create -f -
