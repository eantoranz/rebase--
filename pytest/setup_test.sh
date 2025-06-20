#!/bin/bash

# Run a single test
# first parameter is the name of the script/log file
# second parameter is the descriptive name of the test

# do initialization

set -x

export TEST_DIR=repos/test_$1

./$1.sh &> $1.log &&
  echo Setting up $2 OK || \
  ( echo Setting up $2 failed && exit 1 )
