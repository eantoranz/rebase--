#!/bin/bash

# Copyright (c) 2025 Edmundo Carmona Antoranz
# Released under the terms of GPLv2

set -ex

# Script that will take care building/creating the package

REBASE_DIR=/mnt/work/

cd $REBASE_DIR
  ./run_tests.sh
cd -

echo Tests passed fine