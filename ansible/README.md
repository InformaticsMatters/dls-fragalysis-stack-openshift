# Fragalysis Ansible OpenShift Deployment

## Prerequisites
Before running any playbook: -

1.  A server-compatible `oc` command-set available to you as a user
1.  The OpenShift cluster has been installed
1.  There is an `admin` user known to the cluster
1.  There is a `jenkins` user known to the cluster
1.  You have created a `vault-pass.txt` file in this directory
1.  A Python 3 conda/virtual environment from which to run these playbooks

If using NFS make sure you've configured it with all the appropriate mounts.
If using LocalStorage you must first provision local storage volumes
and run the `local-storage` playbook in order to generate the PVs for use
by applications like the graph database.

You will need to accommodate at least 1,420Gi of disk space. Check the
various `pvc` templates for details.

## Playbooks
Each project is driven by its own set of playbooks, e.g.: -

    $ ansible-playbook playbooks/fragalysis-graph-3/deploy.yaml \
        --vault-password-file vault-pass.txt

## Creating encrypted secrets
If you have the Ansible vault password you can encrypt strings
for the `defauls/main.yaml` file by running something like this: -

    $ ansible-vault encrypt_string <string> \
        --name <string name> --vault-password-file vault-pass.txt
