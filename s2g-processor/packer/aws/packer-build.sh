#!/usr/bin/env bash

# Converts the YAML to JSON and runs the Packer build.
# Alan Christie
# July 2018

set -e

../../../yaml2json.py < nextflow.yml > nextflow.json
packer build nextflow.json
