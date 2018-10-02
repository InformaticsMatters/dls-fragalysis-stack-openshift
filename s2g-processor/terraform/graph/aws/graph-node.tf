resource "aws_instance" "graph-node" {
  ami = "${lookup(var.amis, var.region)}"
  instance_type = "r5.xlarge"
  key_name = "${var.key_name}"
  vpc_security_group_ids = ["${var.efs_ec2_sgid}", "${aws_security_group.neo4j.id}"]
  subnet_id = "${var.subnet}"
  associate_public_ip_address = true
  source_dest_check = false

  root_block_device {
    volume_type = "gp2"
    volume_size = "${var.root_size}"
  }

  tags {
    Name = "graph-node"
  }
}
