# Fraglysis Ansible OpenShift Deployment
To run the playbook you will need to create a `vault-pass.txt` file that
contains the password used to create the vault passwords used in this project.
    
The run the playbook with the command: -

    ansible-playbook -i localhost, --vault-password-file vault-pass.txt \
        site.yaml
