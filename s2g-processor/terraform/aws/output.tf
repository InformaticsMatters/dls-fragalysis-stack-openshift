output "Nextflow" {
  value = "${aws_instance.nextflow-node.0.public_ip}"
}
