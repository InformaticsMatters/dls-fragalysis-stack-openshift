---

# The Graph compiler Ansible inventory file.

all:
  hosts:
    ${nf_host}:

  vars:
    keypair_name: ${keypair_name}
    efs_dns_name: ${efs_dns_name}
    efs_mount: /mnt/efs

    nf_cloud_size: 2
    nf_cloud_name: frag
