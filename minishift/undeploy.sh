#!/usr/bin/env bash

set -e pipefail

oc login -u developer > /dev/null
oc project fragalysis-stack > /dev/null

echo "- Undeploying Application..."

#oc delete all,route --selector template=fs-web
oc delete all,secrets --selector template=fs-cartridge
oc delete all --selector template=fs-db
oc delete all --selector template=fs-graph

echo "- Deleting PVCs..."

#oc delete pvc --selector template=fs-web-pvc
oc delete pvc --selector template=fs-cartridge-pvc
oc delete pvc --selector template=fs-db-pvc
oc delete pvc --selector template=fs-graph-pvc
