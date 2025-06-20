#!/bin/bash

# Copyright (c) 2025 Edmundo Carmona Antoranz
# Released under the terms of GPLv2

# create a rpm image for packaging rebase--

set -e

if [ $# -lt 2 ]; then
  echo Did not provide enough parameters to create rpm builder image
  echo Need to provide:
  echo - Distro
  echo - Distro Docker tag
  echo - Optionally, a requirements file "(packages will be installed with apt-get)"
  exit 1
fi

DISTRO=$1
DOCKER_TAG=$2
REQUIREMENTS_FILE=$3

echo Building rebase-- rpm builder image for $DISTRO:$DOCKER_TAG

(
  echo from $DISTRO:$DOCKER_TAG
  if [ $DISTRO == rockylinux -o $DISTRO == almalinux ]; then
    echo run dnf -y install "'dnf-command(config-manager)'"
    if [ $DOCKER_TAG == 9 ]; then
      echo run dnf -y config-manager --set-enabled crb
    elif [ $DOCKER_TAG == 8 ]; then
      echo run dnf -y config-manager --set-enabled powertools
    fi
    echo run dnf -y install epel-release
    fi
    echo run yum install -y findutils rpmdevtools make git gcc vim indent
    if [ "$REQUIREMENTS_FILE" != "" ]; then
      echo -n run yum install -y
      cat "$REQUIREMENTS_FILE" | while read package; do
        echo -n " $package"
      done
      echo
    fi
) | docker build --tag rebase--rpmbuilder-$DISTRO-$DOCKER_TAG -

echo Finished building the image
