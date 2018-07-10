#!/usr/bin/env bash

START_DIR=$(pwd)

# Terraform
# (form the core node and EFS storage)
echo ">>> Terraform (init/apply)..."
cd terraform/aws
terraform init
terraform apply --auto-approve
cd ${START_DIR}

# Ansible
# (mount EFS, transfer files)
echo ">>> Ansible..."
cd ansible
ansible-playbook site.yml
cd ${START_DIR}

echo ">>> Deployed. Have fun!"
