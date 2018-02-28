#!/usr/bin/env bash

# Makes persistent volumes in minishift.
# See the blog-post "adding-persistent-storage-to-minishift-cdk-3-in-minutes".
# Just run these commands in the minishift ssh environment.

# To get in...
#   minishift ssh
#   sudo -i
#
# Then run...

# pv-fs-neo4j-data
mkdir -p /mnt/sda1/var/lib/minishift/openshift.local.volumes/pv-fs-neo4j-data
mkdir /mnt/sda1/var/lib/minishift/openshift.local.volumes/pv-fs-neo4j-data/registry
chmod 777 -R /mnt/sda1/var/lib/minishift/openshift.local.volumes/pv-fs-neo4j-data

# pv-fs-neo4j-log
mkdir -p /mnt/sda1/var/lib/minishift/openshift.local.volumes/pv-fs-neo4j-log
mkdir /mnt/sda1/var/lib/minishift/openshift.local.volumes/pv-fs-neo4j-log/registry
chmod 777 -R /mnt/sda1/var/lib/minishift/openshift.local.volumes/pv-fs-neo4j-log

# pv-fs-pg-data
mkdir -p /mnt/sda1/var/lib/minishift/openshift.local.volumes/pv-fs-pg-data
mkdir /mnt/sda1/var/lib/minishift/openshift.local.volumes/pv-fs-pg-data/registry
chmod 777 -R /mnt/sda1/var/lib/minishift/openshift.local.volumes/pv-fs-pg-data

# pv-fs-cartridge-data
mkdir -p /mnt/sda1/var/lib/minishift/openshift.local.volumes/pv-fs-cartridge-data
mkdir /mnt/sda1/var/lib/minishift/openshift.local.volumes/pv-fs-cartridge-data/registry
chmod 777 -R /mnt/sda1/var/lib/minishift/openshift.local.volumes/pv-fs-cartridge-data

# pv-fs-web-log
mkdir -p /mnt/sda1/var/lib/minishift/openshift.local.volumes/pv-fs-web-log
mkdir /mnt/sda1/var/lib/minishift/openshift.local.volumes/pv-fs-web-log/registry
chmod 777 -R /mnt/sda1/var/lib/minishift/openshift.local.volumes/pv-fs-web-log

# pv-fs-web-media
mkdir -p /mnt/sda1/var/lib/minishift/openshift.local.volumes/pv-fs-web-media
mkdir /mnt/sda1/var/lib/minishift/openshift.local.volumes/pv-fs-web-media/registry
chmod 777 -R /mnt/sda1/var/lib/minishift/openshift.local.volumes/pv-fs-web-media

# Then..
#   exit
#   exit
