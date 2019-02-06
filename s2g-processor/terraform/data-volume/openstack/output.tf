# -----------------------------------------------------------------------------
# Various outputs (for bastion, compute-cluster and ansible)
# -----------------------------------------------------------------------------

output "Volume" {
  value = "${openstack_blockstorage_volume_v3.nextflow_volume.id}"
}
