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

# Pickup the OC command suite...
eval $(minishift oc-env)

# As system admin...
oc login -u system:admin > /dev/null

# Allow containers to run as root...
oc adm policy add-scc-to-user anyuid -z default > /dev/null

# Create the project?
oc get projects/fragalysis-stack > /dev/null 2> /dev/null
if [ $? -ne 0 ]
then
    echo
    echo "+ Creating Fragalysis Project..."
    oc login -u $USER -p $PASSWORD > /dev/null
    oc new-project fragalysis-stack --display-name='Fragalysis Stack' > /dev/null
fi

oc get sa/$SA > /dev/null 2> /dev/null
if [ $? -ne 0 ]
then
    # Create Diamond-specific service account in the Fragalysys Stack project.
    # To avoid privilege escalation in the default account.
    # An experiment with Service Accounts (unused ATM)
    echo
    echo "+ Creating Service Account..."
    oc login -u system:admin > /dev/null
    oc project fragalysis-stack > /dev/null
    oc create sa $SA 2> /dev/null
    # provide cluster-admin role (ability to launch containers)
    oc adm policy add-cluster-role-to-user cluster-admin -z $SA
    # Allow (legacy) containers to run as root...
    oc adm policy add-scc-to-user anyuid -z $SA
fi

set -e pipefail

echo
echo "+ Creating PVs..."

oc login -u system:admin > /dev/null
oc process -f fs-pv-minishift.yaml | oc create -f -

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
