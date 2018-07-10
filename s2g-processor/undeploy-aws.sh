#!/usr/bin/env bash

set -e

START_DIR=$(pwd)

# Ansible
# (Shutdown the cloud-created cluster)
echo ">>> Ansible (teardown)..."
cd ansible
ansible-playbook site-teardown.yml
cd ${START_DIR}

# Terraform
# (just destroy everything)
echo ">>> Terraform (destroy)..."
cd terraform/aws
terraform destroy --auto-approve
cd ${START_DIR}
