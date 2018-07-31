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
`variables.tf`.

>   You need only run Packer once per region. 

## Starting the compute cluster
Before starting the deployment ensure you've installed the SSH agent
and added your key.

    $ eval $(ssh-agent)
    $ ssh-add ~/.ssh/abc-im
 
Crete the compute cluster with terraform (you can adjust the size
and details from within the `variables.tf` file): -

    $ cd terraform/compute-cluster/aws
    $ terraform init
    $ terraform apply -auto-approve

## Configuring the compute cluster
Here we use ansible to deploy the files, count the EFS volume onto the
compute nodes and start the workers. But first you need to copy the
IP addresses seen when creating the cluster into the `inventory.yml` file.

    $ cd ansible
    $ ansible -m ping all
    $ ansible-playbook site.yml
    
## Destroying the compute cluster
Use terraform from the compute cluster directory: -

    $ cd terraform/compute-cluster/aws
    $ terraform destory -force

## Execution and analysis
This step is currently not automated.

With your cluster running and the EFS mounted on each worker, and each worker
ready (tasks managed by teh ansible playbook) you now just need to get to the
Nextflow `master` and run your analysis.

A typical execution, if the SMILES file has the default name (`origin.smi`),
would be, for a cluster with up to 128 cores: -

    nohup ~/nextflow run graph.nf \
        -executor.queueSize 128 \
        -process.executor ignite \
        -process.scratch \
        -with-docker busybox \
        -with-report \
        -with-trace \
        -with-timeline \
        -cluster.join path:/mnt/efs/cluster &

>   The above is executed on the designated master node from the EFS mount
    directory (i.e. `/mnt/efs`).

If you pull back the graph workflow's timing logfiles you can analyse
the execution times of the individual chunks with the `analyse_timing.py`
module (in the `analysis` directory). It expects to find the timing files in
a results directory in the execution directory.

Collect and archive the timing files from the running results directory
and put them in your home directory: -

    $ cd /mnt/efs
    $ find results -name "*.timing" | xargs tar czf ~/timing.tar.gz

Then pull them back to the `analysis` directory, de-compress and analyse them
with something like the following (replacing the IP address with that of the
machine the archived timings files are on): -

    $ scp -i ~/.ssh/abc-im ec2-user@34.244.122.179:timing.tar.gz timing.tar.gz
    $ gunzip -c timing.tar.gz | tar xopf -
    $ ./analyse_timing.py

### De-duplication
To collect and de-duplicate the calculated results: -

    $ find ./results -name edges.gz -print | xargs gunzip | awk '!x[$0]++' > edges.txt
    $ find ./results -name nodes.gz -print | xargs gunzip | awk '!x[$0]++' > nodes.txt
    $ find ./results -name attributes.gz -print | xargs gunzip | awk '!x[$0]++' > attributes.txt

And compress them: -
    
    $ gzip edges.txt nodes.txt attributes.txt

### Using the ephemeral drive(s)
It's not obvious but is described on the AWS [article]. In summary...
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
