# SMILES to Graph (Neo4J) Processing
This directory contains files used for performance evaluation of
the Fragalysis `graph.nf` process on an AWS cluster. These files
fall generally into: -

-   AWS AMI creation (using Packer)
-   AWS bastion & EFS provisioning and Nextflow cluster creation
    (using Terraform and Ansible) and uploading of test data

## Requirements
-   Python 3
-   Packer
-   Terraform

You will need Python 3 and the requirements in the project's
`requirements.txt` file (which will install ansible).

>   You might want start from a suitable conda or virtualenv environment.

## Packer (AMI creation)
You can build the base AMI, which includes Docker, Nextflow (and Java),
from the `packer/<provider>` directory. The Packer files might be in
my preferred format of YAML. For example, to build an AMS image (form the
`packer/aws` directory) run: -

    $ packer-build.sh

>   For AWS you will need to have defined a number of environment variables,
    namely `TF_VAR_aws_access_key` and `TF_VAR_aws_secret_key`.

Remember the AMI it creates and re-place the value in the terraform
`variables.tf` file (see below).

>   You need only run Packer once per region. 

## Starting the cluster
Before starting the deployment ensure you've installed the SSH agent
and added your key.

    $ eval $(ssh-agent)
    $ ssh-add ~/.ssh/abc-im.pem
 
A shell-script wraps the combined execution of `Terraform` (used )to
instantiate the bastion node and EFS storage etc. and `Ansible` to provision
the EFS mounts, copy data and create the Nextflow cluster: -

    $ ./deploy-aws.sh

## Stopping the cluster
You can use the convenient shell-script which calls `Ansible` to delete the
nextflow cluster before using `terrafform` to destroy the remaining cluster: -

    $ ./undeploy-aws.sh

## Execution and analysis
This step is currently not automated.

With your cluster running you now just need to get to the Nextflow `master`
and run your analysis.

A typical execution, if the SMILES file has the default name (`origin.smi`),
would be: -

    $ nohup ./nextflow run graph.nf \
        --graphMaxForks 144 --chunk 25 -with-docker busybox &

If you pull back the Nextflow logfile (`.nextflow.log`) you can analyse
the execution times of the individual chunks with the `analyse_nf_graph.py`
module (in the `analysis` directory).

To collect and de-duplicate the calculated results: -

    $ find ./work -name edges.txt -print | xargs awk '!x[$0]++' > edges.txt
    $ find ./work -name nodes.txt -print | xargs awk '!x[$0]++' > nodes.txt
    $ find ./work -name attributes.txt -print | xargs awk '!x[$0]++' > attributes.txt

And compress them: -
    
    $ gzip edges.txt nodes.txt attributes.txt

## Using the ephemeral drive(s)
It's not obvious bus is described on the AWS [article]. In summary...
use the `lsblk` command to view your available disk devices and their mount
points (if applicable) to help you determine the correct device name to use.

    $ lsblk
    NAME          MAJ:MIN RM   SIZE RO TYPE MOUNTPOINT
    nvme0n1       259:2    0     8G  0 disk 
    ├─nvme0n1p1   259:3    0     8G  0 part /
    └─nvme0n1p128 259:4    0     1M  0 part 
    nvme2n1       259:1    0 838.2G  0 disk 
    nvme1n1       259:0    0 838.2G  0 disk 

Create a filesystem on the devices: -

    $ sudo mkfs -t ext4 /dev/nvme1n1
    $ sudo mkfs -t ext4 /dev/nvme2n1

Create some suitable mount points and mount the drives:

    $ sudo mkdir /data1
    $ sudo mkdir /data2
    $ sudo mount /dev/nvme1n1 /data1
    $ sudo mount /dev/nvme2n1 /data2
    
Then change ownership: -

    $ sudo chown ec2-user.ec2-user /data1
    $ sudo chown ec2-user.ec2-user /data2

>   These are ephemeral drives and they wil be lost between reboots
    so use them with care. Any important data should be put on an EBS
    volume.

---

[article]: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-using-volumes.html
