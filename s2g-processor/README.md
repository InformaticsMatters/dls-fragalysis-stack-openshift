# SMILES to Graph (Neo4J) Processing
This directory contains files used for performance evaluation of
the Fragalysis `graph.nf` process on an AWS cluster. These files
fall generally into: -

-   AWS AMI creation (using Packer)
-   AWS CLuster creation (using Terraform)
-   Uploading of test data and process execution

## Install Python
You will need Python 3 and the requirements in the project's
`requirements.txt` file.

## Packer
You can build the base AMI, which includes Docker, Nextflow (and Java),
from the `packer/<provider>` directory. The Packer files might be in
my preferred format of YAML. For example, to build an AMS image (form the
`packer/aws` directory) run: -

    $ ../../../yaml2json.py < nextflow.yml > nextflow.json
    $ packer build nextflow.json

>   For AWS you will need to have defined a number of environment variables,
    namely `TF_VAR_aws_access_key` and `TF_VAR_aws_secret_key`.

Remember the AMI it creates and re-place the value in the terraform
`variables.tf` file (see below).

>   You need only run Packer once per region. 

## Terraform
Terraform creates, and destroys, your cluster.

>   Note: - if you have created a new AMI then you need to update the `amis`
    variable vin the `variables.tf` file.
    
To begin, only required once, you need to run, from the `terraforn/<proivider>`
directory: -

    $ terraform init

If you make changes to the terraform files run: -

    $ terraform validate
    
If you're in the `aws` directory, to automatically deploy you cluster
(using a key-pair you've created) for a **c5d.xlarge** (4-core) machine,
run: -

    $ terraform apply -auto-approve \
        -var 'aws_key_name=abc' \
        -var 'node_family=c5d.xlarge'

To destroy any cluster run: -

    $ terraform destory --force

## Execution and analysis
With your cluster running you now need to provide it with the SMILES file
to process and run Nextflow.

A typical execution, if the SMILES file has the default name (`test.smi`),
would be: -

    $ nextflow run graph.nf --graphMaxForks 2 -with-docker busybox

If you pull back the Nextflow logfile (`.nextflow.log`) you can analyse
the execution times of the individual chunks with the `analyse_nf_graph.py`
module (in the `analysis` directory).
    