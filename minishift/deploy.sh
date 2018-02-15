#!/usr/bin/env bash

# Assumes the Application's Persistent Volumes are available
# (which is true for minishift). T deploy outside of minishift
# you need to ensure appropriate PVs have been created.
#
# This deployment also assumes you have a fragalysis container image.
# Normally built from the project's root with something like: -
#
#   $ docker build . -t fragalysis-stack:1.0.0

# As system admin...
oc login -u system:admin > /dev/null

# Allow containers to run as root...
oc adm policy add-scc-to-user anyuid -z default

# Create the project?
oc get projects/fragalysis-stack > /dev/null 2> /dev/null
if [ $? -ne 0 ]
then
    echo "+ Creating Fragalysis Project..."
    oc login -u developer > /dev/null
    oc new-project fragalysis-stack --display-name='Fragalysis Stack' > /dev/null
fi

oc get sa/diamond > /dev/null 2> /dev/null
if [ $? -ne 0 ]
then
    # An experiment with Service Accounts (unused ATM)
    echo "+ Creating Service Account..."
    oc login -u system:admin > /dev/null
    # Create Diamond-specific service account in the Fragalysys Stack project.
    # To avoid privilege escalation in the default account.
    oc create sa diamond
    # provide cluster-admin role (ability to launch containers)
    oc adm policy add-cluster-role-to-user cluster-admin -z diamond
    # Allow (legacy) containers to run as root...
    oc adm policy add-scc-to-user anyuid -z diamond
    # Back to developer
    oc login -u developer > /dev/null
fi

set -e pipefail

# Login as the Fragalysis user...
oc login -u developer > /dev/null

echo "+ Creating PVCs..."

oc process -f ../templates/fs-graph-pvc.yaml | oc create -f -
oc process -f ../templates/fs-db-pvc.yaml | oc create -f -
oc process -f ../templates/fs-cartridge-pvc.yaml | oc create -f -
#oc process -f ../templates/fs-web-pvc.yaml | oc create -f -

echo "+ Deploying Application..."

oc process -f ../templates/fs-graph.yaml | oc create -f -
oc process -f ../templates/fs-db.yaml | oc create -f -
oc process -f ../templates/fs-cartridge.yaml | oc create -f -
#oc process -f ../templates/fs-web.yaml | oc create -f -
