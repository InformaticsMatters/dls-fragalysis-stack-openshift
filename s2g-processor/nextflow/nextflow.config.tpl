// A Terraform template file for
// out Nextflow cloud configuration.

// THIS FILE IS CURRENTLY NOT USED

cloud {
    imageId = '${image_id}'
    userName = 'ec2-user'
    instanceType = 'c5.18xlarge'
    subnetId = '${subnet}'
    securityGroup = '${security_group}'
    bootStorageSize = '8GB'

    sharedStorageId = '${efs_id}'
    sharedStorageMount = '/mnt/efs'

    keyName = '${key_name}'
    keyFile = '~/.ssh/${key_name}.pem'

    spotPrice = '1.5'
}
