# frag-processor/ansible
Ansible scripts used to automate Graph processing stages. 

Pre-requisites: -

You will need...

-   Ansible (ideally a recent 2.7)
-   As we use S3 you will need to define
    -   FRAGALYSIS_S3_BUCKET (=im-fragnet)
    -   AWS_ACCESS_KEY_ID
    -   AWS_SECRET_ACCESS_KEY
 
There are three stages, each with an accompanying shell-script/playbook: -

1.  Standardise
1.  Graph Processing
1.  Combination

Before doing anything you will need to clone this repo and move to this
directory, typically into something like `~/github`: -

    $ mkdir ~/github
    $ cd ~/github
    $ git clone https://github.com/InformaticsMatters/dls-fragalysis-stack-openshift.git
    $ cd dls-fragalysis-stack-openshift/frag-processor/ansible

## Standardising

## Processing
Create a `parameters` file from the template (`parameters.template`),
set suitable values from its examples and any other variables you want to
set and then run: -

    $ ./process.sh

>   For up-to-date documentation refer to the documentation in the
    Ansible playbook `playbook/graph-processor.yaml`.

## Combination

---
 