resource "openstack_compute_instance_v2" "nextflow-node" {
  count = "${var.num_nodes}"
  name = "nextflow-fragnet-${format("%03d", count.index + 1)}"
  availability_zone = "ceph"
  image_name = "nextflow-base-image-3"
  flavor_name = "c2.xlarge"
  key_pair = "${var.key_pair}"
  security_groups = ["default"]

  network {
    name = "${var.network}"
  }
}

resource "openstack_compute_volume_attach_v2" "attached" {
  count = "${var.num_nodes}"
  instance_id = "${element(openstack_compute_instance_v2.nextflow-node.*.id, count.index)}"
  volume_id   = "${var.data_volume_id}"
  multiattach = true
}