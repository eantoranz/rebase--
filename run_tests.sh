#!/bin/bash

# copyright (c) 2025 Edmundo Carmona Antoranz
# Released under the terms of GPLv2

set -ex

cd pytest

dirs=$( ls -1 repos/ | wc -l )

if [ $dirs -gt 0 ]; then
  echo Deleting preexisting test repos
  rm -fR repos/*
fi


# setup of the tests

./setup_test.sh simple_rebase "Simple rebase"

# simple conflict on a file, no changes on the upstream
# rebase should carry over the file as it was in the original merge
./setup_test.sh conflicting_blob_merge_commit "Conflicting blob merge commit"

# a trickier blob merge
# a conflict resolution has to be carried over and the file has been modified in upstream
# so both things have to be in the final file
./setup_test.sh conflicting_blob_merge_commit_change_upstream "Conflicting blob merge commit rebase with change in upstream"

# test rebasing a merge commit where a file is deleted
./setup_test.sh deleted_blob "Deleted BLOB"

# end up with an empty working tree
./setup_test.sh empty_root_dir "Empty root dir"

# a simple merge commit
./setup_test.sh simple_merge_commit "Simple merge commit"

cd -

echo Running tests
python3-coverage run --source rebasedashdash -m pytest pytest/test.py

echo Generating code coverage report && python3-coverage html
