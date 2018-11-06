# Building the cluster
Prerequisites: -

1.  This guide assumes that you have a working OpenShift deployment
1.  The cluster has a suitable  `admin` user
1.  The cluster has a `jenkins` user
1.  You have access to the **bastion** node
1.  `ansible` is installed on the bastion
1.  `python` is installed on the bastion
1.  You have cloned this repository onto the bastion
1.  You have the project’s **Ansible Vault** password
1.  You have suitable credentials to write to the **xchem** Docker Hub registry
1.  Slack is setup to receive notifications from Jenkins
1.  An NFS volume is available on the bastion

There are a number of steps involved, described in the following
sub-sections. Namely: -

*   Create NFS directories
*   Deploy Fragalysis (Dev, Prod, Ric etc.)
*   Install and configure the Jenkins CI/CD framework
*   Run the initial CI/CD Job sequence 

## Step 1 - Create NFS directories
A number of containers depend on pre-allocated (NFS) volumes.
At the time of writing creation of these volumes is not automated,
instead we rely on the pre-allocation of NFS partitions.

Assuming NFS is available on the bastion (at the path `/data`)
you should be able to create the volumes by running the convenient script
in this repository: -

    sudo openshift/mk-nfs-pvs.sh
    
## Step 2 - Deploy Fragalysis
Fragalysis consists of a number of independent **projects** (namespaces)
in OpenShift. The creation and configuration of theses projects is
controlled by a number of Ansible playbooks.

To run the playbooks navigate to this project's `ansible` directory and
create the file `vault-pass.txt`. Put the Ansible Vault password
in it as plain text and then run the following playbook commands...

    ansible-playbook playbooks/fragalysis-dev/deploy.yaml \
        --vault-password-file vault-pass.txt

    ansible-playbook playbooks/fragalysis-prod/deploy.yaml \
        --vault-password-file vault-pass.txt

    ansible-playbook playbooks/fragalysis-stag/deploy.yaml \
        --vault-password-file vault-pass.txt

And, to deploy the MolPort database (which occupies the
Fragalysis Development project) run...

    ansible-playbook playbooks/fragalysis-dev/deploy-molport.yaml \
        --vault-password-file vault-pass.txt \
        --extra-vars "deploy_molport_graph=true"

## Step 3 - Install and configure the Jenkins CI/CD framework
To install and configure the CI/CD framework, follow the instructions in the
document `installing-and-configuring-jenkins.pdf`, which can be found
in this doc directory.

## Step 4 - Run the initial CI/CD Job sequence 
The `configure-cicd.py` utility that you ran as part of the previous step
will have created all of the CI/CD jobs in the Jenkins server but they will
have been delivered in a *disabled* state, waiting for you to enable them.

For the first execution of the CI/CD Jobs to be successful they will need
to be enabled and run in a specific order. From the Jenkins console navigate
to the `All` jobs view and enable and then manually execute the following
jobs: - 

*   `Security Probe`
*   `Fragalysis Backend`
*   `Fragalysis Stack`
*   `Graph Image`

These jobs build key Docker images that are loaded into the OpenShift built-in
registry. Once done enable and run the following...

*   `Web Image`
*   `Web Image (RG)`
*   `Loader Image`
*   `Promote Loader Image (RG)`

Once these Jobs have executed you can then safely enable all the remaining Jobs.

You will then need to promote an image to the production project.

# Oops! I've just deleted the "Dev" project. How do I recover it?

**Don't Panic**. The good news is that pretty-much all of your data is
persisted and your MySQL databases may already be backed up. To recover
the dev project...

1.  **Step 1** above should be unnecessary
1.  Repeat **Step 2** above
1.  You can (A) re-install Jenkins from scratch as above or (B) restore
    the existing installation. Either way you will receive a new Jenkins API
    token. For each option, refer to the brief notes below.
1.  Repeat **Step 4** above

>   You may need/want to recover database contents after repeating step 2 above.
    This is described in the "Restoring Databases" section of the architecture
    document.

## (A) Re-install Jenkins form scratch
To re-install Jenkins you will need to wipe (or move) the contents of the
`pv-fs-jenkins` NFS directory. Once done, simply follow **Step 3** above.

## (B) Recover Jenkins
To accomplish this you will need to move the contents of the existing
`pv-fs-jenkins` NFS directory leaving the existing directory empty as described
below. Then, install Jenkins as described in **Step 3** above bit do not
bother configuring it. All you want is a fresh Jenkins.

*   Copy the persistent data volume. There's a lot of data but just copy it
    somewhere.
*   Remove the data from the existing volume
    (Jenkins will have permissions issues when it starts if you don't)
*   Once Jenkins is available, goto the Jenkins configuration and look for
    the Jenkins URL and Jenkins tunnel values in the `Cloud -> Kubernetes`
    deployment. Take a copy of these. These values will be something like
    `http://172.30.101.45:80` and `172.30.62.196:50000`
*   Scale the Jenkins server down using the OpenShift console.
*   Take a note of the ownership of the existing data in the Jenkins
    persistent volume (it might be something like `1000240000.nfnobody`)
*   Copy the data you kept in step 2 back into the Jenkins persistent volume
*   Make sure all the permission match those found above using
    `sudo chown -R 1000240000.nfsnobody *`
*   Edit the `config.xml` file so that IP values of the `jenkinsUrl` and
    `jenkinsTunnel` properties match those found above
*   Scale the Jenkins server up and check that it starts without
    significant error
*   All the jobs and their build histories should have been restored
*   Check the `buildah-slave` Agent configurations in the
    `Kubernetes Pod Template` section, specifically the volume mounts,
    and `Run in privileged mode` setting.
*   Edit the OpenShift route definition for Jenkins and ensure that
    `openshift.io/host.generated: 'true'` is present
    in the `metatdata -> annotations` block
*   Remove the built-in sample job

---

_Alan Christie_  
_November 2018_
