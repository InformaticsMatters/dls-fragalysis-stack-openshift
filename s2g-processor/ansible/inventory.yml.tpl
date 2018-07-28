---

# The Graph compiler Ansible inventory file.

all:
  vars:
    keypair_name: ${keypair_name}
    efs_id: ${efs_id}
    efs_dns_name: ${efs_dns_name}
    efs_mount: /mnt/efs

worker:
  hosts:
    ${nf_worker_1}:
    ${nf_worker_2}:
    54.246.255.14:
    34.244.183.116:
    54.171.251.96:
    34.255.8.194:

master:
  hosts:
    ${nf_master}:

---

# The Graph compiler Ansible inventory file.

all:
  nodes:
    hosts:
        ${nf_host}:
  master:
    hosts:


    nf_cloud_size: 2
    nf_cloud_name: frag
