# -----------------------------------------------------------------------------
# An EFS instance.
# -----------------------------------------------------------------------------

# For instructions omn settign it up see the guide
# "Walkthrough 1: Create Amazon EFS File System
#                 and Mount It on an EC2 Instance Using the AWS CLI"
#
# At https://docs.aws.amazon.com/efs/latest/ug/wt1-getting-started.html

resource "aws_efs_file_system" "fragalysis" {
  creation_token = "diamond-fragalysis-efs"
}

resource "aws_efs_mount_target" "fragalysis" {
  file_system_id = "${aws_efs_file_system.fragalysis.id}"
  subnet_id = "${var.aws_subnet}"
  security_groups = ["${aws_security_group.efs-mt-sg.id}"]
}