output "Nextflow-Node" {
  value = "${openstack_compute_instance_v2.nextflow-node.*.access_ip_v4}"
}
