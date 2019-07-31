export EXPORT_DIR=/data

cd ${EXPORT_DIR}
# Dev/common
mkdir pv-fs-mysql-data
mkdir pv-fs-mysql-data-backup
mkdir pv-fs-jenkins
mkdir pv-fs-input
mkdir pv-fs-graph-data
mkdir pv-fs-graph-data-loader
mkdir pv-fs-graph-3-data-loader
mkdir pv-fs-graph-logs
mkdir pv-fs-molport-enamine-data
mkdir pv-fs-molport-enamine-data-loader
mkdir pv-fs-molport-logs
mkdir pv-fs-web-media
# Production-specific
mkdir pv-fs-p-mysql-data
mkdir pv-fs-p-mysql-data-backup
mkdir pv-fs-p-web-media
# For Ric Gillams' project
mkdir pv-fs-rg-mysql-data
mkdir pv-fs-rg-web-media
# Staging
mkdir pv-fs-s-mysql-data

chmod -R 777 pv-*
chown -R nfsnobody.nfsnobody pv-*

# Note the use of (rw,sync,no_subtree_check,no_root_squash)
# for the postgres volumes!
# See https://github.com/kubernetes/kubernetes/issues/54601

cd /etc/exports.d/
echo ${EXPORT_DIR}/pv-fs-mysql-data *(rw,no_subtree_check,no_root_squash) >> frag.exports
echo ${EXPORT_DIR}/pv-fs-mysql-data-backup *(rw,root_squash) >> frag.exports
echo ${EXPORT_DIR}/pv-fs-jenkins *(rw,root_squash) >> frag.exports
echo ${EXPORT_DIR}/pv-fs-input *(rw,root_squash) >> frag.exports
echo ${EXPORT_DIR}/pv-fs-graph-data *(rw,root_squash) >> frag.exports
echo ${EXPORT_DIR}/pv-fs-graph-data-loader *(rw,root_squash) >> frag.exports
echo ${EXPORT_DIR}/pv-fs-graph-3-data-loader *(rw,root_squash) >> frag.exports
echo ${EXPORT_DIR}/pv-fs-graph-logs *(rw,root_squash) >> frag.exports
echo ${EXPORT_DIR}/pv-fs-molport-enamine-data *(rw,root_squash) >> frag.exports
echo ${EXPORT_DIR}/pv-fs-molport-enamine-data-loader *(rw,root_squash) >> frag.exports
echo ${EXPORT_DIR}/pv-fs-molport-logs *(rw,root_squash) >> frag.exports
echo ${EXPORT_DIR}/pv-fs-p-mysql-data *(rw,no_subtree_check,no_root_squash) >> frag.exports
echo ${EXPORT_DIR}/pv-fs-p-mysql-data-backup *(rw,root_squash) >> frag.exports
echo ${EXPORT_DIR}/pv-fs-p-web-media *(rw,root_squash) >> frag.exports
echo ${EXPORT_DIR}/pv-fs-rg-mysql-data *(rw,no_subtree_check,no_root_squash) >> frag.exports
echo ${EXPORT_DIR}/pv-fs-rg-web-media *(rw,root_squash) >> frag.exports
echo ${EXPORT_DIR}/pv-fs-s-mysql-data *(rw,no_subtree_check,no_root_squash) >> frag.exports
echo ${EXPORT_DIR}/pv-fs-web-media *(rw,root_squash) >> frag.exports

systemctl restart nfs-server
showmount -e localhost
