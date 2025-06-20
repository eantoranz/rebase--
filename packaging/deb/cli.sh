#!/bin/bash

# Copyright (c) 2025 Edmundo Carmona
# Released under the terms of GPLv2

set -e

cd /mnt/work
# Script that will take care of doing the build process
git config --global --add safe.directory $PWD

echo Current status:
git status
echo Ready to start working

/bin/bash
