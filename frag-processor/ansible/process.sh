#!/usr/bin/env bash

set -e

# The user must have created a 'parameters' file
# (expected by the ansible playbooks).
if [ ! -f parameters ]; then
   echo "The 'parameters' file does not exist."
   exit 1
fi

ansible-playbook playbooks/processor/graph-processor.yaml --extra-vars "@parameters"
