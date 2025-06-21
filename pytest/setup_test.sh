#!/bin/bash

# Run a single test
# first parameter is the name of the script/log file
# second parameter is the descriptive name of the test

# do initialization

set -x

export TEST_DIR=repos/test_$1

bash ./$1.sh &> $1.log &&\
echo Setting up $2 OK &&\
echo commit chart for the test: &>> $1.log &&\
GIT_DIR=$TEST_DIR/.git git log --oneline --graph --all --decorate &>> $1.log ||\
(
  echo Setting up $2 failed
  exit 1
)
