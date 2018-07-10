resource "aws_instance" "nextflow-ephemeral-node" {
  ami = "${lookup(var.amis, var.aws_region)}"
  instance_type = "${var.node_ephemeral_family}"
  count = "${var.num_ephemeral_nodes}"
  key_name = "${var.aws_key_name}"
  vpc_security_group_ids = ["${aws_security_group.efs-ec2-sg.id}"]
  subnet_id = "${var.aws_subnet}"
  associate_public_ip_address = true
  source_dest_check = false

  tags {
    Name = "nf-bastion"
  }
}
