sudo -i

# Mounting the Cinder volume for NFS storage

mkfs -t ext4 /dev/vdc
mkdir /exports-fs
mount /dev/vdc /exports-fs
echo '/dev/vdc /exports-fs ext4  defaults 0 0' >> /etc/fstab

# Creating NFS mounts

cd /exports-fs
mkdir pv-fs-neo4j-data
mkdir pv-fs-neo4j-data-loader
mkdir pv-fs-neo4j-log
mkdir pv-fs-pg-data
mkdir pv-fs-cartridge-data
mkdir pv-fs-web-log
mkdir pv-fs-web-media
chmod -R 777 pv-*
chown -R nfsnobody.nfsnobody pv-*

cd /etc/exports.d/
echo '/exports-fs/pv-fs-neo4j-data *(rw,root_squash)' >> frag.exports
echo '/exports-fs/pv-fs-neo4j-data-loader *(rw,root_squash)' >> frag.exports
echo '/exports-fs/pv-fs-neo4j-log *(rw,root_squash)' >> frag.exports
echo '/exports-fs/pv-fs-pg-data *(rw,root_squash)' >> frag.exports
echo '/exports-fs/pv-fs-cartridge-data *(rw,root_squash)' >> frag.exports
echo '/exports-fs/pv-fs-web-log *(rw,root_squash)' >> frag.exports
echo '/exports-fs/pv-fs-web-media *(rw,root_squash)' >> frag.exports

systemctl restart nfs-server
showmount -e localhost
