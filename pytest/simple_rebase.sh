#!/bin/bash

# The simplest of tests
# a basic rebase of a branch

. init_test.sh

cat > hello_world.txt <<EOF
Hello world

This is the initial commit of the file

Wrapping up the file
EOF

git add hello_world.txt
git commit -m "hello word: initial commit"

cat > hello_world.txt <<EOF
Hello world

We are modifying the middle of the file

Wrapping up the file
EOF

git add hello_world.txt
git commit -m "hello word: modifying the middle of the file"

git switch -c other @~

cat > hello_world.txt <<EOF
Hello world

This is the initial commit of the file

We are modifying the end of the file
EOF

git add hello_world.txt
git commit -m "hello word: modifying the end of the file"

main_commit=$( git rev-parse main )
other_commit=$( git rev-parse HEAD )

git branch test

get_chart
