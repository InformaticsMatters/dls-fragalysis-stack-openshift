# Terraform variables for the graph cluster.
#
# You can change variables from the command line: -
#
#   $ terraform apply -auto-approve -var 'a_node_spot_family=c5d.xlarge'

# -----------------------------------------------------------------------------
# Mandatory Parameters (must be defined externally)
# -----------------------------------------------------------------------------

# ENVIRONMENT VARIABLES
# Define these secrets as environment variables
#
# - TF_VAR_aws_access_key                 Your AWS access token
# - TF_VAR_aws_secret_key                 Your AWS secret key

variable "aws_access_key" {}
variable "aws_secret_key" {}

# -----------------------------------------------------------------------------
# Default Parameters (can be changed via command-line or ENV)
# -----------------------------------------------------------------------------

variable "key_name" {
  description = "The name of the Key Pair, as known by AWS"
  default = "abc-im"
}

variable "region" {
  description = "EC2 Region for the Cluster"
  default = "eu-west-1" # Ireland
}

# The AMIs for our images built with Packer.
variable "amis" {
  description = "AMIs by Region"
  type = "map"
  default = {
    eu-west-1 = "ami-7c322196" # Ireland (im-nf-6)
  }
}

variable "vpc" {
  description = "The Cluster VPC (xchem-vpc)"
  default = "vpc-fcf29e9a"
}

variable "subnet" {
  description = "The Cluster Subnet"
  default = "subnet-a1bc02e9"
}

variable "efs_ec2_sgid" {
  description = "The EFS EC2 Security Group ID"
  default = "sg-2fcc7952"
}

variable "root_size" {
  description = "The size (GiB) of the graph root volumes"
  default = 1200
}
