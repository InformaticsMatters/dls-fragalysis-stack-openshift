# Fragalysis Ansible OpenShift Deployment

## Prerequisites
Before running any playbook: -

1.  The `oc` command-set is available to you as a user
1.  An OpenShift cluster has been installed
1.  There is an `admin` user known to the cluster
1.  There is a `jenkins` user known to the cluster
1.  You have created a `vault-pass.txt` file in this directory

If using NFS make sure you've configured it with all the appropriate mounts.
The playbook will create the PVs and PVCs: -

You will need to accommodate at least 1,420Gi of disk space. Check the
various `pvc` templates for details.
 
## Creating encrypted secrets
If you have the Ansible vault password you can encrypt strings
for the `defauls/main.yaml` file by running something like this: -

    ansible-vault encrypt_string <string> \
        --name <string name> --vault-password-file vault-pass.txt
