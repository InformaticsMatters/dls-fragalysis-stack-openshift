# -----------------------------------------------------------------------------
# Neo4J security group
# -----------------------------------------------------------------------------

resource "aws_security_group" "neo4j" {
  name = "Neo4j Security Group"
  vpc_id = "${var.vpc}"

  ingress {
    from_port = 7474
    to_port = 7474
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port = 7687
    to_port = 7687
    protocol = "tcp"
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
