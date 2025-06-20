#!/bin/bash

# a basic rebase of a merge commit

set -ex

. init_test.sh

cat > hello_world.txt <<EOF
Hello world

This is the initial commit of the file

Wrapping up the file
EOF

git add hello_world.txt
git commit -m "hello word: initial commit"

git branch A
git branch B

cat > hello_world.txt <<EOF
Hello world

We are modifying the middle of the file

Wrapping up the file
EOF

git add hello_world.txt
git commit -m "hello word: modifying the middle of the file"

git switch A
git branch 

cat > hello_world.txt <<EOF
Hello world

A different content from what we have setup in main

Wrapping up the file
EOF

git add hello_world.txt
git commit -m "hello word: also modified the middle of the file"

# now we merge, it should not fail
git checkout main
# this merge has to fail
git merge -m "merging branch A" A || echo Merge failed, as expected

# status has to _not_ be clean at this moment
test $( git status --short | wc -l ) -ne 0 || ( echo Status is clean which is unexpected; git status; exit 1 )

# let's resolve the conflict
# with yet a different content for the file
cat > hello_world.txt <<EOF
Hello world

This is how we solved the conflict

Wrapping up the file
EOF

git add hello_world.txt
git merge --continue

git checkout B

# we add a separate file so we do not mess with the original one
cat > separate-file.txt <<EOF
This is a separate file
EOF

git add separate-file.txt

git commit -m "Adding a separate file"

# new we run the rebase
MAIN_commit=$( git rev-parse main )
A_commit=$( git rev-parse A )
B_commit=$( git rev-parse B )
HEAD_commit=$( git rev-parse @ )

git switch -c test main

echo commit chart for the test:
git log --oneline --graph --all --decorate
