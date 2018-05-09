#!/usr/bin/env bash

# Makes persistent volumes in minishift.
# See the blog-post "adding-persistent-storage-to-minishift-cdk-3-in-minutes".
# Just run these commands in the minishift ssh environment.

# To get in...
#   minishift ssh
#   sudo -i
#
# Then run...

# pv-fs-pg-data
mkdir -p /mnt/sda1/var/lib/minishift/openshift.local.volumes/pv-fs-pg-data
mkdir /mnt/sda1/var/lib/minishift/openshift.local.volumes/pv-fs-pg-data/registry
chmod 777 -R /mnt/sda1/var/lib/minishift/openshift.local.volumes/pv-fs-pg-data

# pv-fs-cartridge-data
mkdir -p /mnt/sda1/var/lib/minishift/openshift.local.volumes/pv-fs-cartridge-data
mkdir /mnt/sda1/var/lib/minishift/openshift.local.volumes/pv-fs-cartridge-data/registry
chmod 777 -R /mnt/sda1/var/lib/minishift/openshift.local.volumes/pv-fs-cartridge-data

# pv-graph-source-data
mkdir -p /mnt/sda1/var/lib/minishift/openshift.local.volumes/pv-graph-source-data
mkdir /mnt/sda1/var/lib/minishift/openshift.local.volumes/pv-graph-source-data/registry
chmod 777 -R /mnt/sda1/var/lib/minishift/openshift.local.volumes/pv-graph-source-data

# Then..
#   exit
#   exit
