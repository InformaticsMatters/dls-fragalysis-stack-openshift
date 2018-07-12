output "Nextflow-Spot" {
  value = "${aws_spot_instance_request.nextflow-spot-node.*.public_ip}"
}

output "Nextflow-EBS" {
  value = "${aws_instance.nextflow-ebs-node.*.public_ip}"
}

output "Nextflow-Ephemeral" {
  value = "${aws_instance.nextflow-ephemeral-node.*.public_ip}"
}

output "EFS-DNS-Name" {
  value = "${aws_efs_file_system.fragalysis.dns_name}"
}