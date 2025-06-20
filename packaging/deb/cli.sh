#!/bin/bash

# Copyright (c) 2025 Edmundo Carmona
# Released under the terms of GPLv2

set -e

# Script that will take care of doing the build process
git config --global --add safe.directory /mnt/work

echo Current status:
git status
echo Ready to start working

/bin/bash
