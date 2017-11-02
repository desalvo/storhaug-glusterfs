#!/bin/bash

VERSION="${1}"
HEADREL="${2:-1}"
SPEC="${3:-scripts/storhaug-glusterfs.spec}"

pushd `git rev-parse --show-toplevel`

tar -czvf storhaug-glusterfs-${VERSION}.tar.gz --transform='s/^src/storhaug-glusterfs/' src/*

rpmbuild -bs -D 'rhel 6' -D "_topdir `pwd`" -D "_sourcedir ." -D "dist .el6.centos" ${SPEC}
rpmbuild -bs -D 'rhel 7' -D "_topdir `pwd`" -D "_sourcedir ." -D "dist .el7.centos" ${SPEC}
rm -f storhaug-glusterfs-${VERSION}.tar.gz

rm -rf repo
mkdir -p repo/el6
mkdir -p repo/el7
sudo mock -r epel-6-x86_64 --resultdir repo/el6/ SRPMS/storhaug-glusterfs-${VERSION}-${HEADREL}.el6.centos.src.rpm
sudo mock -r epel-7-x86_64 --resultdir repo/el7/ SRPMS/storhaug-glusterfs-${VERSION}-${HEADREL}.el7.centos.src.rpm
createrepo repo/el6/
createrepo repo/el7/

rm -f repo/*/*.log
rm -rf BUILD/ BUILDROOT/ RPMS/ SPECS/ SRPMS/

popd
