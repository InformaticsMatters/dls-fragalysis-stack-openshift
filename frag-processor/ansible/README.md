# frag-processor/ansible
Ansible scripts used to automate Graph processing stages. 

Pre-requisites: -

You will need...

-   Git
-   Ansible (ideally a recent 2.7)
-   Python 3 (and pip)
-   As we use S3 you / define
    -   `AWS_ACCESS_KEY_ID`
    -   `AWS_SECRET_ACCESS_KEY`
 
There are three stages, each with an accompanying shell-script/playbook: -

1.  Collection of _raw_ data
1.  Standardise
1.  Graph Processing
1.  Combination

Before doing anything you will need to clone this repo and move to this
directory, typically into something like `~/github`: -

    $ mkdir ~/git
    $ cd ~/git
    $ git clone https://github.com/InformaticsMatters/dls-fragalysis-stack-openshift.git
    $ cd dls-fragalysis-stack-openshift/frag-processor/ansible

## Collecting new (raw) data
Everything starts with the vendor's files. We call these 'raw' files from the
fragment-processing perspective. These need to be collected and placed on
a suitable path on **s3** under `raw`.

For example, if you have new MolPort (SMILES) data and have downloaded it
you can _sync_ it to **s3**. In the following example the current directory
contains MolPort SMILES data for 2019-05. We sync this to **s3** with the
following command: -

    $  aws s3 sync . s3://im-fragnet/raw/vendor/molport/2019-05
 
>   Use of the AWS command-line will require suitable credentials,
    recorded in environment variables.

## Standardising
All raw files are processed into our _standard_ file format
before further processing.

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

>   The default nextflow processing timeout is 5 days (7,200 minutes).
    If you think you need more than 5 days provide a value for
    `nextflow_timeout_minutes` in you parameters file.

## Graph Processing
Standard files are compiled into graph representations, called a _build_.

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

>   The default nextflow processing timeout is 5 days (7,200 minutes).
    If you think you need more than 5 days provide a value for
    `nextflow_timeout_minutes` in you parameters file.

## Combination
_Builds_ can be combined to form a graph containing molecules
from multiple vendors.

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
 