# Building the cluster
Requirements: -

1.  This guide assumes that you have a working OpenShift deployment
1.  The cluster has a suitable  `admin` user
1.  The cluster has a `jenkins` user
1.  You have access to the **bastion** node
1.  `ansible` is installed on the bastion
1.  `python` is installed on the bastion
1.  You have cloned this repository onto the bastion
1.  You have the project’s **Ansible Vault** password
1.  You have suitable credentials to write to the xchem Docker Hub registry
1.  Slack is setup to receive notifications from Jenkins
1.  An NFS volume is available on the bastion

There are a number of steps to cover. Namely: -

*   Create NFS directories
*   Deploy Fragalysis (Dev, Prod, Ric etc.)
*   Install and configure the Jenkins CI/CD framework
*   Run the initial CI/CD Job sequence 

## Create NFS directories
A number of containers depend on pre-allocated (NFS) volumes.
At the time of writing creation of these volumes is not automated,
instead we rely on the pre-allocation of NFS partitions.

Assuming an NFS volume in available on the bastion (at the path `/data`)
you should be able to create the NFS volumes by running the convenient script
in this repository: -

    sudo openshift/mk-nfs-pvs.sh
    
## Deploy Fragalysis
Fragalysis consists of a number of independent **projects** (namespaces)
in OpenShift. The creation and configuration of theses projects is
controlled by a number of Ansible playbooks contained in this repository.

Navigate to this project's `ansible` directory.
 
Create the file `vault-pass.txt` and put the Ansible Vault password
in it as plain text and then run the following Ansible commands...

    ansible-playbook playbooks/fragalysis-dev/deploy.yaml \
        --vault-password-file vault-pass.txt

    ansible-playbook playbooks/fragalysis-prod/deploy.yaml \
        --vault-password-file vault-pass.txt

    ansible-playbook playbooks/fragalysis-stag/deploy.yaml \
        --vault-password-file vault-pass.txt

Ans, to deploy the MolPort database (which happens to cocupy the
Development project) run...

    ansible-playbook playbooks/fragalysis-dev/deploy-molport.yaml \
        --vault-password-file vault-pass.txt \
        --extra-vars "deploy_molport_graph=true"

## Install and configure the Jenkins CI/CD framework
It's an older document, not converted to markdown, you you'll need to follow
the instructions in the document `installing-and-configuring-jenkins.pdf`
that you will find in this doc directory.

## Run the initial CI/CD Job sequence 
The `configure-cicd.py` utility that you ran as part of the previous step
will have created all of the CI/CD jobs in the Jenkins server but they will
have been delivered in a *disabled* state, waiting for you to enable them.

To be successful, for the first execution the Jobs will need to be enabled and
run in a specific order. From the Jenkins console navigate to the
`All` jobs view and enable and execute the following jobs: - 

*   `Security Probe`
*   `Fragalysis Backend`
*   `Fragslysis Stack`
*   `Graph Image`

These jobs build key Docker images that are loaded into the OpenShift built-in
registry. Once done enable and run the following...

*   `Web Image`
*   `Web Image (RG)`
*   `Loader Image`
*   `Promote Loader Image (RG)`

Once these Jobs have executed you can then safely enable all the remaining Jobs.

You will then need to promote an image to the production project.
