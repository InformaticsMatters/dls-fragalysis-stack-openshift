output "Graph-Nodes" {
  value = "${aws_instance.graph-node.0.public_ip}"
}
