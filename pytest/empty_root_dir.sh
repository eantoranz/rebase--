#!/bin/bash

# will create one directory with 2 files.
# will create one branch from here.
# On each one of those two branches, one
# different file will be deleted.
# On main, a third file will be added.
# then the file will be deleted.
# Then the two non-main branches will be merged
# that should produce an empty root dir.

# then a rebase on main~ will be done
# which will end up with a single file on the working tree
# then a rebase on main will be done and it should end up with an empty working tree

. init_test.sh

mkdir a-dir
cat > a-dir/A.txt <<EOF
Content of file A
EOF

cat > a-dir/B.txt <<EOF
Content of file B
EOF

git add a-dir

git commit -m "First commit with 2 files"

git branch A
git branch B

cat > a-dir/C.txt <<EOF
Content of file C
EOF

git add a-dir
git commit -m "Adding C.txt"

git rm a-dir/C.txt
git commit -m "Removinf C.txt"

git switch A
git rm a-dir/A.txt
git commit -m "Removing A.txt"

git switch B
git rm a-dir/B.txt
git commit -m "Removing B.txt"

git switch -c test

git merge A -m "Merging A" # there should be no conflict there...

# working tree should be empty

test $( git ls-tree -r HEAD | wc -l ) -eq 0 || ( echo working tree is not empty which is unexpected; git ls-tree -r HEAD; exit 1 )

get_chart
