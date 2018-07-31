resource "aws_instance" "nextflow-bastion-node" {
  ami = "${lookup(var.amis, var.region)}"
  instance_type = "t2.small"
  key_name = "${var.key_name}"
  vpc_security_group_ids = ["${var.efs_ec2_sgid}"]
  subnet_id = "${var.subnet}"
  associate_public_ip_address = true
  source_dest_check = false

  root_block_device {
    volume_type = "gp2"
    volume_size = "8"
  }

  tags {
    Name = "nf-bastion-ebs"
  }
}
