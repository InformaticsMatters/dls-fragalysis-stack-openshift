# Terraform variables for the nextflow cluster.
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
  default = "sg-6406cd18"
}

variable "spot_root_size" {
  description = "The size (GiB) of spot instance root volumes"
  default = 32
}

# -----------------------------------------------------------------------------
# Spot instance node configuration (type A)
# -----------------------------------------------------------------------------

variable "num_spot_a_nodes" {
  description = "The number of Nextflow Spot nodes for our A-types"
  default = 7
}

variable "a_node_spot_family" {
  description = "The machine family (i.e. t2.large)"
  default = "c5.2xlarge"
}

variable "a_node_spot_price" {
  description = "The spot bid price"
  default = "0.19"
}

# -----------------------------------------------------------------------------
# Spot instance node configuration (type B)
# -----------------------------------------------------------------------------

variable "num_spot_b_nodes" {
  description = "The number of Nextflow Spot nodes for our B-types"
  default = 0
}

variable "b_node_spot_family" {
  description = "The machine family (i.e. t2.large)"
  default = "c5.9xlarge"
}

variable "b_node_spot_price" {
  description = "The spot bid price"
  default = "1.0"
}
