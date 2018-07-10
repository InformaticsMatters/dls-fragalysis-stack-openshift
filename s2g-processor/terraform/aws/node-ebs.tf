resource "aws_instance" "nextflow-ebs-node" {
  ami = "${lookup(var.amis, var.aws_region)}"
  instance_type = "${var.node_ebs_family}"
  count = "${var.num_ebs_nodes}"
  key_name = "${var.aws_key_name}"
  vpc_security_group_ids = ["${aws_security_group.efs-ec2-sg.id}"]
  subnet_id = "${var.aws_subnet}"
  associate_public_ip_address = true
  source_dest_check = false

  root_block_device {
    volume_type = "gp2"
    volume_size = "${var.node_ebs_size}"
  }

  tags {
    Name = "nf-bastion"
  }
}
