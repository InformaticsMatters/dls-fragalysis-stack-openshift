resource "aws_spot_instance_request" "nextflow-spot-node" {
  ami = "${lookup(var.amis, var.aws_region)}"
  instance_type = "${var.node_spot_family}"
  count = "${var.num_spot_nodes}"
  key_name = "${var.aws_key_name}"
  vpc_security_group_ids = ["${var.aws_efs_ec2_sgid}"]
  subnet_id = "${var.aws_subnet}"
  associate_public_ip_address = true
  source_dest_check = false
  spot_price = "${var.node_spot_price}"
  spot_type = "one-time"
  wait_for_fulfillment = true

  tags {
    Name = "nf-spot"
  }
}
