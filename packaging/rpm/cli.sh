#!/bin/bash

# Copyright (c) 2025 Edmundo Carmona
# Released under the terms of GPLv2

set -e

# Script that will set us in a "usable" environment
cd /mnt/work
git config --global --add safe.directory $PWD

echo Current status:
git status
echo Ready to start working

/bin/bash
