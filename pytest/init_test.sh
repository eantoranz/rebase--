#!/bin/bash

# the same basic stuff for all tests

set -xe

if [ -d $TEST_DIR ]; then
  rm -fR $TEST_DIR
fi

git init -b main $TEST_DIR
cd $TEST_DIR

export GIT_EDITOR=/bin/true
git config user.name "Fulanito D'Tal"
git config user.email fulanito@foo.bar

function get_chart {
  echo commit chart for the test:
  git log --oneline --graph --all --decorate
}