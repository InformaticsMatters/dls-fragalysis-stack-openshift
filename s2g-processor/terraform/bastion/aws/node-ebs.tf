resource "aws_instance" "nextflow-bastion-node" {
  ami = "${lookup(var.amis, var.region)}"
  instance_type = "c5d.2xlarge"
  key_name = "${var.key_name}"
  vpc_security_group_ids = ["${aws_security_group.ec2-sg.id}"]
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
