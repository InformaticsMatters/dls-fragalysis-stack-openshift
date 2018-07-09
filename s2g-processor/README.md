# SMILES to Graph (Neo4J) Processing
This directory contains files used for performance evaluation of
the Fragalysis `graph.nf` process on an AWS cluster. These files
fall generally into: -

-   AWS AMI creation (using Packer)
-   AWS Cluster creation (using Terraform)
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
(using a key-pair you've created) for a **c5.xlarge** (4-core) machine,
run: -

    $ terraform apply -auto-approve \
        -var 'node_ebs_family=c5.xlarge'

A 72-core **c5.18xlarge** system can be started with: -

    $ terraform apply -auto-approve \
        -var 'node_ebs_family=c5.18xlarge'

To destroy any cluster run: -

    $ terraform destory --force

### Using the ephemeral drive(s)
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

## Preparing the EFS volumes
With Terraform complete you should be able to run the Ansible playbook
that mounts the EFS volume onto the host ECS instance and then
uploads and unpacks any data files you've put in the `smiles` directory.

To prepare the EFS volume, run the following from the `ansible` directory...

    $ ansible-playbook -i inventory.yml site.yml

## Nextflow cluster
To create hthe cmpute cluster to analyser your data use Nextflow.
From the `nextflow` directory you can create you a cluster (named **frag**)
that has 2 nodes with the command: -

    $ nextflow cloud create frag -c 2 -y

## Execution and analysis
With your cluster running you now just need to get to the Nextflow master
ans run your analysis.

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

---

[article]: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-using-volumes.html
