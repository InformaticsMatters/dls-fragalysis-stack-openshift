# -----------------------------------------------------------------------------
# Template file transformations
# -----------------------------------------------------------------------------
# The template file is rendered by the "template_file" action
# and written out by the "local_file" action.

# ------------------
# Ansible Inventrory
# ------------------
data "template_file" "ansible-inventory" {
  template = "${file("${var.ansible_dir}/inventory.yml.tpl")}"

  vars {
    nf_host = "${aws_spot_instance_request.nextflow-spot-node.0.public_ip}"
    efs_id = "${aws_efs_file_system.fragalysis.id}"
    efs_dns_name = "${aws_efs_file_system.fragalysis.dns_name}"
    keypair_name = "${var.aws_key_name}"
  }
}

resource "local_file" "ansible-inventory" {
  content = "${data.template_file.ansible-inventory.rendered}"
  filename = "${var.ansible_dir}/inventory.yml"
}

# ---------------
# Nextflow Config
# ---------------
data "template_file" "nextflow-config" {
  template = "${file("${var.nextflow_dir}/nextflow.config.tpl")}"

  vars {
    image_id = "${lookup(var.amis, var.aws_region)}"
    subnet = "${var.aws_subnet}"
    security_group = "${aws_security_group.efs-ec2-sg.id}"
    efs_id = "${aws_efs_file_system.fragalysis.id}"
    key_name = "${var.aws_key_name}"
  }
}

resource "local_file" "nextflow-config" {
  content = "${data.template_file.nextflow-config.rendered}"
  filename = "${var.nextflow_dir}/nextflow.config"
}
