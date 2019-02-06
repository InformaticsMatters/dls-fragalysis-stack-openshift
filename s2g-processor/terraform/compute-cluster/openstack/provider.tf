# -----------------------------------------------------------------------------
# Lock to a specific Terraform release (for now)
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Configure our OpenStack Connection
# -----------------------------------------------------------------------------

provider "openstack" {
  user_name = "${var.os_username}"
  region = "${var.os_region_name}"
  tenant_name = "${var.os_project_name}"
  domain_name = "${var.os_user_domain_name}"
  password = "${var.os_password}"
  auth_url = "${var.os_auth_url}"
  version = "1.14.0"
}

# -----------------------------------------------------------------------------
# Other providers
# -----------------------------------------------------------------------------

provider "local" {
  version = "1.1.0"
}

provider "template" {
  version = "1.0.0"
}
