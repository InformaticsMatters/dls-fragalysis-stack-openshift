# -----------------------------------------------------------------------------
# Various outputs (for bastion, compute-cluster and ansible)
# -----------------------------------------------------------------------------

output "EFS-DNS-Name" {
  value = "${aws_efs_file_system.fragalysis.dns_name}"
}
output "EFS Mount Target SG" {
  value = "${aws_security_group.efs-mt-sg.id}"
}
output "EFS EC2 SG" {
  value = "${aws_security_group.efs-ec2-sg.id}"
}
