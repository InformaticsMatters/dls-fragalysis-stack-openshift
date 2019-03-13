#!/usr/bin/env bash

set -e

# The user must have created a 'parameters' file
# (expected by the ansible playbooks).
if [ ! -f parameters ]; then
   echo "The 'parameters' file does not exist."
   exit 1
fi

# You will need to set...
: "${AWS_SECRET_ACCESS_KEY?Need to set AWS_SECRET_ACCESS_KEY}"
: "${AWS_ACCESS_KEY_ID?Need to set AWS_ACCESS_KEY_ID}"

ansible-playbook playbooks/processor/standardise.yaml --extra-vars "@parameters"
