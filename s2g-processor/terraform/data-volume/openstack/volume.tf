resource "openstack_blockstorage_volume_v3" "nextflow_volume" {
  region      = "${var.os_region_name}"
  name        = "nextflow-fragnet-volume"
  size        = "${var.volume_size_g}"
}
