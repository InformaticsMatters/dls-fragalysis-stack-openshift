output "Nextflow-Spot" {
  value = "${aws_spot_instance_request.nextflow-spot-node.*.public_ip}"
}
