#!/bin/bash

# Copyright (c) 2025 Edmundo Carmona Antoranz
# Released under the terms of GPLv2

set -ex

rpmdev-setuptree

# Script that will take care building/creating the package

REBASE_DIR=/mnt/work

TARGET_DIR=$REBASE_DIR/packages/files/rebase---$VERSION

if [ ! -d $TARGET_DIR ]; then
	mkdir -p $TARGET_DIR
fi

# let's create the package every single time so we make sure we are _not_ working on a preexisting (and potentially busted!!!) file
git config --global --add safe.directory "$REBASE_DIR" # so that git can work without complaining
cd $REBASE_DIR
git archive --format=tar.gz --prefix=rebase---"$VERSION"/ -o $TARGET_DIR/rebase---$VERSION.tar.gz $COMMITTISH -- rebase-- README\* rebasedashdash.py
cp $TARGET_DIR/rebase---$VERSION.tar.gz ~/rpmbuild/SOURCES/rebase--

PYTHON_VERSION=$( python3 -c "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}')" )
echo python version: $PYTHON_VERSION
sed "s/%PYTHON_VERSION%/${PYTHON_VERSION}/" packaging/rpm/files/rebase--.spec.in > ~/rpmbuild/SPECS/rebase--.spec

while true; do
  PACKAGE_ERROR=0
  rpmbuild --define "debug_package %{nil}" -ba ~/rpmbuild/SPECS/rebase--.spec || PACKAGE_ERROR=1
  if [ $PACKAGE_ERROR -eq 0 ]; then
    break
  fi
  echo Something failed creating deb package
  echo You can try any adjustment necessary to try to get the package to build successfully.
  echo If you run \"exit 0\", a new attempt to build the package will be carried out.
  echo If you run \"exit 1\", no more attempts will be tried and packaging process will be halted.
  /bin/bash || ( echo Halting packaging process; exit 1 )
done

ARCH=$( uname -m )

# making sure that the package can be installed
yum install -y /root/rpmbuild/RPMS/$ARCH/*.rpm && rebase-- --help > /dev/null || ( echo rebase-- rpm package installation test failed; exit 1 )
echo Package can be installed without issues, binary is present in \$PATH

rpm -qpi /root/rpmbuild/RPMS/$ARCH/rebase---*.rpm
cp -v /root/rpmbuild/RPMS/$ARCH/*.rpm $REBASE_DIR/

cd "$REBASE_DIR"

echo Finished building rebase-- version $VERSION packages for $DISTRO $DOCKER_TAG from committish $COMMITTISH

ls -l *.rpm

echo Thanks for using rebase-- rpm packager.
