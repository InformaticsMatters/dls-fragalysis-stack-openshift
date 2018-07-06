# -----------------------------------------------------------------------------
# Template file transformations
# -----------------------------------------------------------------------------
# The template file is rendered by the "template_file" action
# and written out by the "local_file" action.

data "template_file" "inventory" {
  template = "${file("${var.ansible_dir}/inventory.yml.tpl")}"

  vars {
    nf_host = "${aws_instance.nextflow-ebs-node.public_ip}"
  }
}

resource "local_file" "inventory" {
  content = "${data.template_file.inventory.rendered}"
  filename = "${var.ansible_dir}/inventory.yml"
}
