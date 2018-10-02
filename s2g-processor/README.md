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
        -executor.queueSize 256 \
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

    cd /mnt/efs
    find results -name "*.timing" | xargs tar czf ~/timing.tar.gz

Then pull them back to the `analysis` directory, de-compress and analyse them
with something like the following (replacing the IP address with that of the
machine the archived timings files are on): -

    MASTER=54.72.6.187
    scp -i ~/.ssh/abc-im ec2-user@${MASTER}:timing.tar.gz timing.tar.gz
    gunzip -c timing.tar.gz | tar xopf -
    ./analyse_timing.py

### Preserving Jun2018 run data
Archiving to S3 from one of the compute nodes,
given a run (i.e. run number 7): -

-   Create a `dls-fragalysis/analysis/Jun2018_${RUN}` S3 directory
-   Create a `dls-fragalysis/analysis/Jun2018_${RUN}/results` S3 directory

A typical workflow would be (from the master instance): -

    aws configure
    
    RUN=7
    
    cd /mnt/efs
    mv .nextflow.log Jun2018_${RUN}.nextflow.log
    mv nohup.out Jun2018_${RUN}.nohup.out
    mv report.html Jun2018_${RUN}.report.html
    mv timeline.html Jun2018_${RUN}.timeline.html
    mv trace.txt Jun2018_${RUN}.trace.txt
    gzip origin.smi

    mv results Jun2018_${RUN}.results
    
    aws s3 cp Jun2018_${RUN}.nextflow.log s3://dls-fragalysis/analysis/Jun2018_${RUN}/
    aws s3 cp Jun2018_${RUN}.nohup.out s3://dls-fragalysis/analysis/Jun2018_${RUN}/
    aws s3 cp Jun2018_${RUN}.report.html s3://dls-fragalysis/analysis/Jun2018_${RUN}/
    aws s3 cp Jun2018_${RUN}.timeline.html s3://dls-fragalysis/analysis/Jun2018_${RUN}/
    aws s3 cp Jun2018_${RUN}.trace.txt s3://dls-fragalysis/analysis/Jun2018_${RUN}/
    aws s3 cp graph.nf s3://dls-fragalysis/analysis/Jun2018_${RUN}/
    aws s3 cp origin.smi.gz s3://dls-fragalysis/analysis/Jun2018_${RUN}/
    
    aws s3 sync Jun2018_${RUN}.results s3://dls-fragalysis/analysis/Jun2018_${RUN}/results

### De-duplication
To collect and de-duplicate the calculated results: -

    RUN=7
    SORT=gsort
    time (export LC_ALL=C; zcat *.attributes.gz | ${SORT} -S16G --parallel=16 --temporary-directory=/data1/tmp -u  > ../attributes.${RUN}.txt)
    time (export LC_ALL=C; zcat *.nodes.gz | ${SORT} -S16G --parallel=16 --temporary-directory=/data1/tmp -u  > ../nodes.${RUN}.txt)

Deduplicating the files in 5 attempts, the following typically takes about 3-4 minutes per item...

    time (export LC_ALL=C; zcat *.edges.gz | ${SORT} -S16G --parallel=16 --temporary-directory=/data1/tmp -u > ../edges.${RUN}.txt)

    (export LC_ALL=C; find results-${RUN} -name "*[01].smi.edges.gz" -print | xargs gzip -dc | ${SORT} -S16G --parallel=16 -u > edges.01.txt)
    (export LC_ALL=C; find results-${RUN} -name "*[23].smi.edges.gz" -print | xargs gzip -dc | ${SORT} -S16G --parallel=16 -u > edges.23.txt)
    (export LC_ALL=C; find results-${RUN} -name "*[45].smi.edges.gz" -print | xargs gzip -dc | ${SORT} -S16G --parallel=16 -u > edges.45.txt)
    (export LC_ALL=C; find results-${RUN} -name "*[67].smi.edges.gz" -print | xargs gzip -dc | ${SORT} -S16G --parallel=16 -u > edges.67.txt)
    (export LC_ALL=C; find results-${RUN} -name "*[89].smi.edges.gz" -print | xargs gzip -dc | ${SORT} -S16G --parallel=16 -u > edges.89.txt)

>   The `awk` approach above takes about 3 minutes whereas the `gsort` (OSX)
    or more general sort takes about 24 seconds (`-S8G --parallel=4`),
    6-times faster. Using the 8-cores on a Mac has little effect.

`awk` is fast for small files, the following typically takes about 5 minutes per item...

    cat edges.0.txt edges.1.txt | awk '!x[$0]++' > edges.01.txt
    cat edges.2.txt edges.3.txt | awk '!x[$0]++' > edges.23.txt
    cat edges.4.txt edges.5.txt | awk '!x[$0]++' > edges.45.txt
    cat edges.6.txt edges.7.txt | awk '!x[$0]++' > edges.67.txt
    cat edges.8.txt edges.9.txt | awk '!x[$0]++' > edges.89.txt

Experimenting with `gsort`, these take about 2 minutes,
with the final one taking 2m41s: -

    (export LC_ALL=C; cat edges.01.txt edges.23.txt | gsort -S8G --parallel=4 -u > edges.0123.txt)
    (export LC_ALL=C; cat edges.45.txt edges.67.txt | gsort -S8G --parallel=4 -u > edges.4567.txt)
    (export LC_ALL=C; cat edges.4567.txt edges.89.txt | gsort -S8G --parallel=4 -u > edges.456789.txt)
    (export LC_ALL=C; cat edges.0123.txt edges.456789.txt | gsort -S8G --parallel=4 -u > edges.0123456789.txt)
    
On Set no. 7 the de-duplication results are: -

    Edges      147,080,409 lines > 75,422,302
    Nodes       57,895,779 lines > 15,781,290
    Attributes   5,000,000 lines > (No gain)

Grand script: -

    time (export LC_ALL=C; zcat *.nodes.gz

Preparing for CSV. With a `nodes.txt`, `edges.txt` and `attributes.txt` file
in a `directory` you can generate the final DB files with: -

    colate_all.py --input_dir directory
    
And compress them: -
    
    gzip edges.${RUN}.txt nodes.${RUN}.txt attributes.${RUN}.txt

Combining original (5.3Million) with new output...
The original set has 5,377,750 nodes and 24,416,356 edges

    (export LC_ALL=C; cat 2018-06-05/nodes.csv results-7-out/nodes.csv | gsort -S8G --parallel=4 -u > combined/nodes.csv)
    (export LC_ALL=C; cat 2018-06-05/edges.csv results-7-out/edges.csv | gsort -S8G --parallel=4 -u > combined/edges.csv)

### Using EC2 ephemeral drive(s)
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

## Neo4J performance tuning
You can start an instance using the terraform config in `terraform/graph/aws`.
Initial deployment used a `r5.xlarge` instance type.

This relies on a pre-exiting VPC, subnet and security group. Once started
(it uses our nextflow packer image) you need to: -

-   Install the S3 files
-   Launch neo4j

### Install S3 files
Login to the instance and, armed with AWS credentials,
you can get the CSV files from S3: -

    $ ssh -i ~/.ssh/abc-im ec2-user@<ip>
    $ mkdir loaded-data data-loader logs
    $ cd data-loader
    $ aws configure
    [...]
    $ aws s3 sync s3://dls-fragalysis/analysis/Jun2018_FINAL_plus/graph .
    $ gzip -d nodes.csv.gz edges.csv.gz
    $ chmod +x *.sh
 
Allow sufficient time for the final `gzip` decompression stage,
this can take a few minutes.
   
### Launch neo4j
Assuming you have a valid `N_USER` and `N_PASSWORD` environment variables
you can start the neo4j container and import the data with this command: -

    $ docker run -d --publish=7474:7474 --publish=7687:7687 \
        -v $HOME/data-loader:/data-loader \
        -v $HOME/loaded-data:/loaded-data \
        -v $HOME/logs:/graph-logs \
        -e NEO4J_dbms_memory_pagecache_size=16g \
        -e NEO4J_dbms_memory_heap_initial__size=8g \
        -e NEO4J_dbms_memory_heap_max__size=8g \
        -e NEO4J_dbms_directories_data=/loaded-data \
        -e NEO4J_dbms_directories_logs=/graph-logs \
        -e NEO4H_AUTH=${N_USER}:${N_PASSWORD} \
        -e NEO4J_EDITION=community \
        -e EXTENSION_SCRIPT=/data-loader/load_neo4j.sh \
        neo4j:3.4.5

>   The demo instance uses the Diamond cluster developer credentials
    as neo4j authentication.

>   It is safe to restart the container once started as the `load-neo4j.sh`
    script detects the presence of  an imported database and therefore does
    not try to import once restarted.

---

[article]: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-using-volumes.html
