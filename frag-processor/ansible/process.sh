#!/usr/bin/env bash

set -e

if [ ! -f parameters ]; then
   echo "The 'parameters' file does not exist."
   exit 1
fi

ansible-playbook playbooks/processor/graph-processor.yaml --extra-vars "@parameters"
