resource "aws_security_group" "efs-ec2-sg" {
  name = "EFS EC2 SG"
  description = "SG for EC2 instance"
  vpc_id = "${var.aws_vpc}"

  # SSH in
  ingress {
    protocol = "tcp"
    from_port = 22
    to_port = 22
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Any outbound traffic
  egress {
    protocol = "-1"
    from_port = 0
    to_port = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "efs-mt-sg" {
  name = "EFS Mount Target SG"
  description = "SG for mount target"
  vpc_id = "${var.aws_vpc}"

  # NFS from EC2
  ingress {
    protocol = "tcp"
    from_port = 2049
    to_port = 2049
    security_groups = ["${aws_security_group.efs-ec2-sg.id}"]
  }

  # Any outbound traffic
  egress {
    protocol = "-1"
    from_port = 0
    to_port = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
}
