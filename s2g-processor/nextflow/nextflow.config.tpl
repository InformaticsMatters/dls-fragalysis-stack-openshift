cloud {
    imageId = 'ami-4b7daa32'
    userName = 'ec2-user'
    instanceType = 't2.large'
    subnetId = '${subnet}'
    securityGroup = '${security_group}'
    bootStorageSize = '8GB'

    sharedStorageId = '${efs_id}'
    sharedStorageMount = '/mnt/efs'

    keyName = '${key_name}'
    keyFile = '~/.ssh/${key_name}.pem'

    spotPrice = '1.5'
}
