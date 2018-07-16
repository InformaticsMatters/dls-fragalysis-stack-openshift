resource "aws_spot_instance_request" "nextflow-spot-b-node" {
  ami = "${lookup(var.amis, var.region)}"
  instance_type = "${var.b_node_spot_family}"
  count = "${var.num_spot_b_nodes}"
  key_name = "${var.key_name}"
  vpc_security_group_ids = ["${var.efs_ec2_sgid}"]
  subnet_id = "${var.subnet}"
  associate_public_ip_address = true
  source_dest_check = false
  spot_price = "${var.b_node_spot_price}"
  spot_type = "one-time"
  wait_for_fulfillment = true

  root_block_device {
    volume_type = "gp2"
    volume_size = "${var.spot_root_size}"
  }

  tags {
    Name = "nf-spot-b"
  }
}
