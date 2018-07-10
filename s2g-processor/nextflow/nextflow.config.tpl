cloud {
    imageId = 'ami-02ffefe8'
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
