output "Nextflow-Spot-A" {
  value = "${aws_spot_instance_request.nextflow-spot-a-node.*.public_ip}"
}
output "Nextflow-Spot-B" {
  value = "${aws_spot_instance_request.nextflow-spot-b-node.*.public_ip}"
}
