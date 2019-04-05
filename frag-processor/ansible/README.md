# frag-processor/ansible
Ansible scripts used to automate Graph processing stages. 

Pre-requisites: -

You will need...

-   Git
-   Ansible (ideally a recent 2.7)
-   Python 3 (and pip)
-   As we use S3 you / define
    -   AWS_ACCESS_KEY_ID
    -   AWS_SECRET_ACCESS_KEY
 
To install Python 3 (and pip) on CentOS...

    $ sudo yum install -y epel-release
    $ sudo yum install -y python36 python36-pip
    $ sudo ln -s /usr/bin/python3.6 /usr/bin/python3

>   If singularity is installed after this you might find it installs
    Python 3.4 and breaks any links you have to 3.6. If so just remake them
    with something like `sudo ln -sf /usr/bin/python3.6 /usr/bin/python3`
    
There are three stages, each with an accompanying shell-script/playbook: -

1.  Standardise
1.  Graph Processing
1.  Combination

Before doing anything you will need to clone this repo and move to this
directory, typically into something like `~/github`: -

    $ mkdir ~/git
    $ cd ~/git
    $ git clone https://github.com/InformaticsMatters/dls-fragalysis-stack-openshift.git
    $ cd dls-fragalysis-stack-openshift/frag-processor/ansible

## Standardising
Create a `parameters` file from the template (`parameters.template`),
set suitable values from its examples and any other variables you want to
set and then run the following, and inspect the progress with
`tail`: -

    $ cp parameters.template parameters
    [edit parameters]
    $ nohup ./run-standardise.sh &
    $ tail -f nohup.out

>   For up-to-date documentation refer to the documentation in the
    Ansible playbook `playbooks/processor/standardise.yaml`.

## Graph Processing
Create a `parameters` file from the template (`parameters.template`),
set suitable values from its examples and any other variables you want to
set and then run the following, and inspect the progress with
`tail`: -

    $ cp parameters.template parameters
    [edit parameters]
    $ nohup ./run-graph-processor.sh &
    $ tail -f nohup.out

>   For up-to-date documentation refer to the documentation in the
    Ansible playbook `playbooks/processor/graph-processor.yaml`.

## Combination
Create a `parameters` file from the template (`parameters.template`),
set suitable values from its examples and any other variables you want to
set and then run the following, and inspect the progress with
`tail`: -

    $ cp parameters.template parameters
    [edit parameters]
    $ nohup ./run-combiner.sh &
    $ tail -f nohup.out

>   For up-to-date documentation refer to the documentation in the
    Ansible playbook `playbooks/processor/standardise.yaml`.

---
 