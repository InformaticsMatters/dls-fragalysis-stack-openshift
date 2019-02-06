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

variable "volume_size_g" {
  description = "The volume size"
  default = 40
}
