---

# The Graph compiler Ansible inventory file.

all:
  hosts:
    ${nf_host}:

  vars:
    efs_dns_name: ${efs_dns_name}
