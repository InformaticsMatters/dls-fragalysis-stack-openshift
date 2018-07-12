---

# The Graph compiler Ansible inventory file.

all:
  nodes:
    hosts:
        ${nf_host}:
  master:
    hosts:

  vars:
    keypair_name: ${keypair_name}
    efs_id: ${efs_id}
    efs_dns_name: ${efs_dns_name}
    efs_mount: /mnt/efs

    nf_cloud_size: 2
    nf_cloud_name: frag
