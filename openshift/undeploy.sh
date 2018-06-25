#!/usr/bin/env bash

set -e pipefail

#oc login -u admin > /dev/null
oc project fragalysis-cicd > /dev/null

echo
echo "- Undeploying Application..."

oc delete all --selector template=fs-db-backup
oc delete all,route --selector template=fs-web
#oc delete all,secrets --selector template=fs-cartridge
oc delete all --selector template=fs-db
oc delete all --selector template=fs-graph

echo
echo "- Removing Secrets..."

oc delete secrets --selector template=fs-secrets

echo
echo "- Deleting PVCs..."

#oc delete pvc --selector template=fs-cartridge-pvc
oc delete pvc --selector template=fs-db-backup-pvc
oc delete pvc --selector template=fs-db-pvc

echo
echo "- Deleting PVs..."

oc delete pv --selector template=fs-pv-nfs
