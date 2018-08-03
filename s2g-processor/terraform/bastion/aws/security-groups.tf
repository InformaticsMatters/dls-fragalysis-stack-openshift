# -----------------------------------------------------------------------------
# Essential EFS/EC2 security groups
# -----------------------------------------------------------------------------

resource "aws_security_group" "ec2-sg" {
  name = "EC2 SG"
  description = "SG for EC2 instance"
  vpc_id = "${var.vpc}"

  # SSH in
  ingress {
    protocol = "tcp"
    from_port = 22
    to_port = 22
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Open to receive anything from anyone (internally)...
  ingress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    self = true
  }

  # Any outbound traffic
  egress {
    protocol = "-1"
    from_port = 0
    to_port = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
}
