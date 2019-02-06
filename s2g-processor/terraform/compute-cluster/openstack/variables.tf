# -----------------------------------------------------------------------------
# Mandatory Parameters (must be defined externally)
# -----------------------------------------------------------------------------

# ENVIRONMENT VARIABLES
# Define these secrets as TF_VAR_ environment variables

variable "os_auth_url" {}
variable "os_password" {}
variable "os_project_name" {}
variable "os_region_name" {}
variable "os_user_domain_name" {}
variable "os_username" {}

# -----------------------------------------------------------------------------
# Default Parameters (can be changed via command-line or ENV)
# -----------------------------------------------------------------------------

variable "num_nodes" {
  description = "The number of Nextflow nodes"
  default = 2
}

variable "key_pair" {
  description = "The KeyPair name known to the provider"
  default = "stfc-abc-1"
}

variable "network" {
  description = "The Network name"
  default = "xchem-private"
}

variable "data_volume_id" {
  description = "The shared data volume"
  default = "7b5a03ff-51b8-434b-a8fb-e2a2d2ae43e8"
}
