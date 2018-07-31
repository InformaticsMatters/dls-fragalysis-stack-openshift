output "Nextflow-Bastion" {
  value = "${aws_instance.nextflow-bastion-node.0.public_ip}"
}
