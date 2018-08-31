# Fraglysis Ansible OpenShift Deployment
To run the playbook you will need to create a `vault-pass.txt` file that
contains the password used to create the vault passwords used in this project.
    
The run the playbook with the command: -

    ansible-playbook -i localhost, \
        --vault-password-file vault-pass.txt \
        site.yaml

And, to also install the backup process...

    ansible-playbook -i localhost, \
        --extra-vars "deploy_backup=true" \
        --vault-password-file vault-pass.txt \
        site.yaml

And, to also install the Jun2018 Graph database...

    ansible-playbook -i localhost, \
        --extra-vars "deploy_jun2018_graph=true" \
        --vault-password-file vault-pass.txt \
        site.yaml

## Prerequisites
Before running the playbook: -

1.  You're on the bastion node
1.  The `oc` command-set is available to you as a user
1.  An OpenShift cluster has been installed
1.  There is an `admin` user known to the cluster
1.  There is a `jenkins` user known to the cluster
1.  You have created a `vault-pass.txt` file in this directory

If using NFS the following NFS volumes are required for a _full_ installation
on the bastion `/data` directory: -

*   fs-input
*   pv-fs-graph-data
*   pv-fs-graph-data-loader
*   pv-fs-graph-logs
*   pv-fs-jenkins
*   pv-fs-mysql-data
*   pv-fs-mysql-data-backup

You will need to accommodate at least 1,420Gi of disk space. Check the
various `pvc` templates for details.
 
## Creating encrypted secrets
If you have the ansible vault password you can encrypt strings
for the `secrets.yaml` file by running something like this: -

    ansible-vault encrypt_string <string> \
        --name <string name> --ask-vault-pass
