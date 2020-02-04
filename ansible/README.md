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

### Creating new Stack deployments

A project replicates what you see in the **PROD** project, which contains the
following significant OpenStack/Kubernetes objects: -

-   A **persistent volume** (and **claim**) for the stack loader's data.
-   A **deployment** of MySQL
-   A **deployment** of the stack's Docker image (built by Jenkins)
-   Dynamic **volumes** for MySQL data the stack's media
-   Numerous **secrets**

There are other objects (like Pods/Jobs for the loader and probe) but the
above represents the significant (visible) items.

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

2.  Create `deploy.yaml` and `undeploy,.yaml` files in your new directory.
    You can copy the files from `playbooks/fragalysis-stack-prod-im` as these
    will contain all the information we need.
    
        cp playbooks/fragalysis-stack-prod-im/*.yaml \
            playbooks/fragalysis-stack-prod-${PRJ_NAME}

3.  Edit your new `deploy.yaml` and define values for the variables: -
    
    - `namespace` (a unique lower-case tag like `fragalysis-<name>`)
    - `namespace_display_name`
    - `namespace_description`
    - `input_vol_name` (typically using the `<name>` from your namespace)
    - `web_hostname` (typically using the `<name>` from your namespace)
    
4.  Edit your `undeploy.yaml` ansible playbook and replace the values for the
    following variables (this will match the ones you used for the
    `deploy.yaml`): -
 
    - `namespace`
    - `input-vol-name`

5.  As we currently do not use build-chain tools that support
    ARG-before-FROM you will need to create a Dockerfile in the
    project's `images/web` directory with the suffix `<name>` from your
    namespace. Crucially the `FROM` line in that Dockerfile must
    use a tag that matches the `<name>`.
 
6.  Add, commit and push all your files to revision control.

7.  Think - before deploying you **MUST** make sure that you have defined
    **NEW AND UNIQUE** values for your `namespace`. If you forget to set the
    `namespace` properly you could damage an existing deployment.
    **ALL PROJECTS MUST HAVE THEIR OWN (UNIQUE) NAMESPACES**.
    
With the above steps satisfied, the `PRJ_NAME` environment variable set,
an active login to the OpenShift cluster in place and a `vault-pass.txt` file
you can deploy the new project with the following Ansible command: -

    ansible-playbook \
        playbooks/fragalysis-stack-prod-${PRJ_NAME}/deploy.yaml \
        --vault-password-file vault-pass.txt

This will create the project in OpenShift and all the related objects.
The project's MySQL database container will be running but the stack container
relies on Jenkins jobs, which build the various stack images based on the git
repositories you define as their source. All this is described in the next
section.

In the meantime, (if you wish) you can test destroying your shiny new OpenShift
project with the following playbook: -

    ansible-playbook \
        playbooks/fragalysis-stack-prod-${PRJ_NAME}/undeploy.yaml \
        --vault-password-file vault-pass.txt
    
### Create the Jenkins view (and its jobs)
In order to deploy the project-specific stack container image you will need
to replicate and adjust a few jobs that run in the Jenkins CI/CD project.

1.  Navigate to the [Jenkins CICD] console for your OpenShift deployment
    and login.

1.  To create a more organised Job workspace, create a _view_ for your project
    by selecting the **New View** option from the Jenkins side-bar and provide
    something project-specific following the pattern
    **Fragalysis (Dev-${PRJ_NAME})**, using the upper-case version of the name
    by convention.
    
    It should be a **List View**.

    Click the **Use a regular expression to include jobs into the view** option
    so the view will automatically include all the jobs we'll be creating. Use
    the pattern `^.* \(${PRJ_NAME}\)$`, i.e. if you've created an `im` project
    the pattern should be `^.* \(IM\)$` (here we use upper-case by convention).
    
    Fill our the **Description** field you you're inclined an then hit **OK***. 
 
1.  Now you just need to replicate a number of existing jobs, using
    a naming convention so they're included in your new view. The jobs you'll
    need to copy are: -
    
    - Fragalysis Backend
    - Fragalysis Frontend
    - Fragalysis Stack
    - Web Image
    
    To copy a Job you simply create a new Job (_Item_) and provide one
    of the jobs listed above as the **Copy from** field.
    
    For example, to copy the **Fragalysis Backend** for your new project
    (where the `PRJ_NAME` is `im`): -
    
    1.  Select **New Item** from the Jenkins console side-panel
    1.  Enter `Fragalysis Backend (IM)` into the **Enter an item name** field
    1.  In the **Copy from** field, enter `Fragalysis Backend`
    1.  Click **OK** 
    1.  Enter a **Description**
    1.  In the **Build Triggers** section click **Disable this project** to
        temporarily disable the job.
    1.  Click **Save**
    1.  If you have named the Job according to the regular expression used to
        setup your project's _view_ the project should now appear (disabled)
        in that view.
        
    Repeat these steps to create project-based jobs for each of the required
    projects.

1.  We now need to configure the parameters of each of the copied jobs
    before we can enable them.
    
    1.  In _your_ new `Fragalysis Backend (*)` job set the following
        **Pipeline** section variables accordingly: -
        
        - `Repository URL`
        - `Branch Specifier (blank for 'any')`
        
        Enable the Job (by de-selecting the **Disable this project**
        option in the **Build Triggers** section) and click **Save**.
        
        As the Job runs periodically in the background, once saved, a new
        Jenkins **Build** will start after a minute or two. You'll see its
        activity in the **Build Executor Status** section of the Jenkins
        side-panel.
        
    1.  In _your_ new `Fragalysis Frontend (*)` job set the following
        **Pipeline** section variables accordingly: -
        
        - `Repository URL`
        - `Branch Specifier (blank for 'any')`

        Enable the Job and save it as before.

    1.  In _your_ new `Fragalysis Stack (*)` job set the following
        **Pipeline** section variables accordingly: -
        
        - `Repository URL`
        - `Branch Specifier (blank for 'any')`

        Set the following **Build Triggers** section variables: -
        
        -   `Projects to watch` should be the comma-separated Job names of your
            Backend and Frontend jobs.
        
        Set the following **Parameters** (found in the upper-part of the
        Job specification): -
        
        -   The `Default Value` of the **FE_GIT_PROJECT** parameter must be
            the Git namespace of your Frontend project
        -   The `Default Value` of the **IMAGE_TAG** parameter should be
            your project namespace, i.e. the value of your `PRJ_NAME`.

        Enable the Job and save it as before.

    1.  In _your_ new `Web Image (*)` job set the following
        **Build Triggers** section variables: -
        
        -   `Projects to watch` should be the Job name of your Stack job.

        Set the following **Parameters**: -
        
        -   The `Default Value` of the **PROJECT** parameter must be
            the namespace of your project
        -   The `Default Value` of the **PROJECT_H** parameter should be
            something that identifies your project.
        -   The `Default Value` of the **PROBE_LOCATION** parameter should be
            the value you used in your project's Ansible playbook
            `web_hostname` variable, prefixed with `https://`
        -   The `Default Value` of the **DOCKERFILE** parameter should be
            the name of the Dockerfile in your images/web directory
            you created when making the changes to deploy the project.

        Enable the Job and save it as before.

1.  With jobs configured we need to wait for the `Web Image` job to run
    before we can load data into the MySQL database.
    
    Once the `Web Image` has run and the container image has initialised you
    can run the **Loader** by manually triggering the existing
    `Promote Loader Image` Jenkins job.
    
    The loader job pauses before actually running, allowing you to specify the
    namespace of the target project that will be loaded. Here you enter the
    namespace of your project (i.e. the `PRJ-NAME` value you used when creating
    the project). Finally, to start the loader hit **Build**.
    
    You can monitor the loader progress by observing the log for the loader
    `Pod` that is created in your OpenShift project.

1.  Once you've setup your Jenkins jobs you can optionally _get_ them as XML
    into this project using the `configure-cicd.py` script in the `jenkins`
    directory. Once fetched you can add and commit the files to revision
    control so that they can be restored from the fetched content if needed.
    
    To fetch the Jenkins configuration (which includes the jobs and the view)
    run the following (from the `jenkins`) directory: -
    
        ./configure-cicd.py get

    Views and jobs are written to the `views` and `jobs` directories
    respectively.
    
    Add, commit and push any changes.
    
## Creating encrypted secrets
If you have the Ansible vault password you can encrypt strings
for the `defauls/main.yaml` file by running something like this: -

    ansible-vault encrypt_string <string> \
        --name <string name> --vault-password-file vault-pass.txt

---

[jenkins cicd]: https://jenkins-fragalysis-cicd.apps.xchem.diamond.ac.uk
