#!/bin/bash

# Copyright (c) 2025 Edmundo Carmona Antoranz
# Released under the terms of GPLv2

# create a deb image for packaging rebase--

set -e

if [ $# -lt 2 ]; then
	echo Did not provide enough parameters to create deb builder image
	echo Need to provide:
	echo - Distro
	echo - Distro Docker tag
	echo - Optionally, a requirements file "(packages will be installed with apt-get)"
	exit 1
fi

DISTRO=$1
DOCKER_TAG=$2
REQUIREMENTS_FILE=$3

echo Building rebase-- deb builder image for $DISTRO:$DOCKER_TAG

(
	echo from $DISTRO:$DOCKER_TAG
	echo run apt-get update
	echo run apt-get install -y build-essential git vim gdb devscripts debhelper indent
	if [ -n "$REQUIREMENTS_FILE" ]; then
		echo -n run apt-get install -y
		cat "$REQUIREMENTS_FILE" | while read package; do
			echo -n " $package"
		done
		echo
	fi
) | docker build --tag rebase--debbuilder-$DISTRO-$DOCKER_TAG -

echo Finished building the image
