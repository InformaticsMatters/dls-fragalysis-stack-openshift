#!/usr/bin/env bash

# User
OS_DEVELOPER_USER=diamond

set -e pipefail

oc login -u OS_DEVELOPER_USER -p $OS_DEVELOPER_PASSWORD > /dev/null
oc project fragalysis-stack > /dev/null

echo
echo "- Undeploying Application..."

oc delete all,route --selector template=fs-web
oc delete all,secrets --selector template=fs-cartridge
oc delete all --selector template=fs-db
oc delete all --selector template=fs-graph

echo
echo "- Removing Secrets..."

oc delete secrets --selector template=fs-secrets

echo
echo "- Deleting Loaders..."

oc delete all --selector template=fs-web-media-loader
oc delete all --selector template=fs-neo4j-data-loader

echo
echo "- Deleting PVCs..."

oc delete pvc --selector template=fs-web-pvc
oc delete pvc --selector template=fs-cartridge-pvc
oc delete pvc --selector template=fs-db-pvc
oc delete pvc --selector template=fs-graph-pvc

echo
echo "- Deleting PVs..."

oc login -u admin -p $OS_ADMIN_PASSWORD > /dev/null
oc delete pv --selector template=fs-pv-nfs
