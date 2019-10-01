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

    ansible-playbook playbooks/fragalysis-graph-3/deploy.yaml \
        --vault-password-file vault-pass.txt

The following playbooks are _deprecated_: -
 
-  `fragalysis-graph-1`
-  `fragalysis-graph-2`

## Deploying a new Fragalysis Stack project
To deploy a new fragalysis stack project (i.e. a namespace) for
another fragalysis stack (i.e. one other than the standard **DEV**
and **PROD** stacks) you will need to address two deployment areas: -
 
-   Create Ansible 2.7 **playbooks** (variables) that will be used to create
    the OpenShift project (namespaces) and all the related OpenShift objects
    required to satisfy the Stack. Don't worry, most if the work is already
    done, you simply have to define a few variables to _personalise_ the
    project.
-   Create Jenkins **jobs** to automate the stack build process. This
    essentially requires you to copy an existing Jenkins _view_ and
    _personalise_ the jobs in it.

>   These instruction assume that you're not setting up a backup policy for
    the project's MySQL database. That's really only required for the main
    **DEV** and **PROD** projects and not required (or expected) for
    developer-specific projects.

>   The following assumes you already have a viable/working deployment of
    the essential **DEV** and **PROD** projects.

### Create the Ansible playbooks (and their variables)

A project replicates what you see in the **PROD** project, which contains the
following significant OpenStack/Kubernetes objects: -

-   A **persistent volume** (and **claim**) for the stack loader's data.
-   A **deployment** of MySQL
-   A **deployment** of the stack's Docker image (built by Jenkins)
-   Dynamic **volumes** for MySQL data the stack's media
-   Numerous **secrets**

There are other objects (like Pods/Jobs for the  loader and probe but the
above represent the significant (visible) items.

To create and deploy a new project there are number of steps to satisfy: -
 
1.  Create a playbook directory and link to the `roles` directory
    from within it. Use `playbooks/fragalysis-stack-prod-im` as an example.
    If it's for the user `blob` the directory should be called
    `playbooks/fragalysis-stack-prod-blob`. From the project root you
    could run the following: -
    
        PRJ_NAME=blob
        cd ansible
        mkdir playbooks/fragalysis-stack-prod-${PRJ_NAME}
        pushd playbooks/fragalysis-stack-prod-${PRJ_NAME}
        ln -s ../../roles .
        popd
    
    Each new project uses the **PROD** project's Ansible files but defines
    user-specific values for the variables it uses (i.e. the project/namespace
    name amongst other things).

1.  Create `deploy.yaml` and `undeploy,.yaml` files in your new directory.
    You can copy the files from `playbooks/fragalysis-stack-prod-im` as these
    will contain all the information we need.
    
        cp playbooks/fragalysis-stack-prod-im/*.yaml \
            playbooks/fragalysis-stack-prod-${PRJ_NAME}

1.  Edit your new `deploy.yaml` and define values for the variables: -
    
    - `namespace` (a unique lower-case tag)
    - `namespace_display_name`
    - `namespace_description`
    - `input_vol_name` (typically `fs-<namespace>-input`)
    
1.  Edit your `undeploy.yaml` ansible playbook and replace the values for the
    following variables (this will match the ones you used for the
    `deploy.yaml`): -
 
    - `namespace`
    - `input-vol-name`

Add, commit and push all your files to revision control.

Before deploying you **MUST** make sure that you have defined
**NEW AND UNIQUE** values for your `namespace`. 

>   **EXTREME CAUTION**: If you forget to set the
    `namespace` properly you could damage an existing deployment.
    **ALL PROJECTS MUST HAVE THEIR OWN (UNIQUE) NAMESPACES**.
    
With the above steps satisfied (and the `PRJ_NAME` environment variable set)
you can deploy the new project: -

    ansible-playbook \
        playbooks/fragalysis-stack-prod-${PRJ_NAME}/deploy.yaml \
        --vault-password-file vault-pass.txt

..and (if you wish) destroy it with the following: -

    ansible-playbook \
        playbooks/fragalysis-stack-prod-${PRJ_NAME}/undeploy.yaml \
        --vault-password-file vault-pass.txt
    
### Create the Jenkins view (and its jobs)

## Creating encrypted secrets
If you have the Ansible vault password you can encrypt strings
for the `defauls/main.yaml` file by running something like this: -

    ansible-vault encrypt_string <string> \
        --name <string name> --vault-password-file vault-pass.txt
