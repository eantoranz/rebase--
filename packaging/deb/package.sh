#!/bin/bash

# Copyright (c) 2025 Edmundo Carmona Antoranz
# Released under the terms of GPLv2

set -ex

# Script that will take care building/creating the package

REBASE_DIR=/mnt/work/

TARGET_DIR=$REBASE_DIR/packages/files/rebase---$VERSION

function get_distro_version_suffix {
	if [ -f /etc/lsb-release ]; then
		. /etc/lsb-release
		echo $DISTRIB_RELEASE
	elif [ -f /etc/debian_version ]; then
		cat /etc/debian_version | head -n 1 | sed 's/\./u/' # take the first line only, just in case
	else
		echo Could not find distro version suffix "(no lsb-release or debian_version file in /etc)" >&2
	fi
}

cd $REBASE_DIR
  ./run_tests.sh
cd -

if [ ! -d $TARGET_DIR ]; then
	mkdir -p $TARGET_DIR
fi

mkdir /root/DEBBUILD

# let's create the package every single time so we make sure we are _not_ working on a preexisting (and potentially busted!!!) file
git config --global --add safe.directory "$REBASE_DIR" # so that git can work without complaining
git config --global --add safe.directory /mnt/work # so that git can work without complaining
cd $REBASE_DIR
git archive --format=tar.gz --prefix=rebase---"$VERSION"/ -o $TARGET_DIR/rebase---$VERSION.tar.gz $COMMITTISH -- rebase-- README\* rebasedashdash.py
cp $TARGET_DIR/rebase---$VERSION.tar.gz /root/DEBBUILD/rebase--_$VERSION.orig.tar.gz

cd /root/DEBBUILD
tar zxvf rebase--_$VERSION.orig.tar.gz
cd rebase---$VERSION
cp -Rv "$REBASE_DIR"/packaging/deb/files debian

# adjust version in changelog
# find out the short name of the distro to use in the version
DISTRO_VERSION_SUFFIX=$( get_distro_version_suffix )
if [ "$DISTRO_VERSION_SUFFIX" == "" ]; then
	# error message has been provided already in the function, no need to elaborate
	exit 1
fi

DISTRO_PACKAGE_VERSION_SUFFIX=${DISTRO:0:3}${DISTRO_VERSION_SUFFIX}
echo Package distro version suffix: $DISTRO_PACKAGE_VERSION_SUFFIX

sed -i "s/rebase-- (\(.*\)) \(.*\)/rebase-- (\1+$DISTRO_PACKAGE_VERSION_SUFFIX) \2/" debian/changelog

echo current directory: $PWD
echo list of files over here:
find ./ -type f
while true; do
  PACKAGE_ERROR=0
  DEB_BUILD_OPTIONS=noddebs debuild -us -uc || PACKAGE_ERROR=1
  if [ $PACKAGE_ERROR -eq 0 ]; then
    break
  fi
  echo Something failed creating deb package
  echo You can try any adjustment necessary to try to get the package to build successfully.
  echo If you run \"exit 0\", a new attempt to build the package will be carried out.
  echo If you run \"exit 1\", no more attempts will be tried and packaging process will be halted.
  /bin/bash || ( echo Halting packaging process; exit 1 )
done

# making sure that the package can be installed
apt install -y ../*.deb && rebase-- --help > /dev/null || ( echo rebase-- deb package installation test failed; bash; exit 1 )
echo Package can be installed without issues, binary is present in \$PATH

cp -v ../*.deb $REBASE_DIR/

cd "$REBASE_DIR"

echo Finished building rebase-- version $VERSION packages for $DISTRO $DOCKER_TAG from committish $COMMITTISH

ls -l *.deb

echo Thanks for using rebase-- deb packager.
