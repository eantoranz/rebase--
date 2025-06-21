#!/bin/bash

# a basic rebase of a merge commit

. init_test.sh

cat > executable <<EOF
This is an executable file

This is the initial commit of the file

Wrapping up the file
EOF
chmod +x executable

cat > non-executable <<EOF
This is a non-executable file

This is the initial commit of the file

Wrapping up the file
EOF

cat > final-executable-from-main <<EOF
This file will be turned into executable from main branch
EOF

cat > final-executable-from-A <<EOF
This file will be turned into executable from main A
EOF


git add executable non-executable final-executable-from-main final-executable-from-A
git commit -m "Adding an executable and a non-executable file, also two files that will will only change their executable flags (one from each branch)"

git branch A
git branch B

cat > executable <<EOF
This is an executable file

Modifying the middle of the file in main... we will make it non-executable

Wrapping up the file
EOF
chmod -x executable

cat > non-executable <<EOF
This is a non-executable file

This is the initial commit of the file

Modifying the end of the file in main
EOF

chmod +x final-executable-from-main

git commit -m "executable content is modified and changed to non-executable, non-executable is only modified in content, executable-from-ain is turned into executable" executable non-executable final-executable-from-main

test $( git status --short | wc -l ) -eq 0 || ( echo working tree is not clean, which is unexpected; git status; exit 1 )

git switch A
test -x executable || ( echo file 'executable' is not executable after the switch to A which is unexpected; exit 1 )
test -x non-executable && ( echo file 'non-executable' is executable after the switch to A which is unexpected; exit 1 )

cat > executable <<EOF
This is an executable file

This is the initial commit of the file

Modifying the end of the file in A
EOF

cat > non-executable <<EOF
This is a non-executable file

Modifying the middle of the file in A... we will make it executable

Wrapping up the file
EOF
chmod +x non-executable

chmod +x final-executable-from-A

git commit -m "non-executable content is modified and changed to executable, executable is only modified in content, also executable-from-A is made into executable" executable non-executable final-executable-from-A

test $( git status --short | wc -l ) -eq 0 || ( echo working tree is not clean, which is unexpected; git status; exit 1 )

# now we merge, it should not fail
git checkout main
git merge -m "merging branch A" A || ( echo merge of A into main is not expected to fail; git status; exit 1 )

# let's verify the content of the file, just in case
cat > executable <<EOF
This is an executable file

Modifying the middle of the file in main... we will make it non-executable

Modifying the end of the file in A
EOF

cat > non-executable <<EOF
This is a non-executable file

Modifying the middle of the file in A... we will make it executable

Modifying the end of the file in main
EOF

# verifying the executable/non-executable state
test -x executable && ( echo file 'executable' is executable after the merge which is unexpected; exit 1 )
test -x non-executable || ( echo file 'non-executable' is not executable after the merge which is unexpected; exit 1 )
test -x final-executable-from-main || ( echo file 'final-executable-from-A' is not executable after the merge which is unexpected; exit 1 )
test -x final-executable-from-A || ( echo file 'final-executable-from-main' is not executable after the merge which is unexpected; exit 1 )

test $( git status --short | wc -l ) -eq 0

git checkout B

# we add a separate file so we do not mess with the original ones
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

exit 0

# let's run a real rebase
rebase-- B -4r # rebasing for real

test $( git rev-parse main ) == $MAIN_commit && echo main commit did not move
test $( git rev-parse A ) == $A_commit && echo branch A did not move
test $( git rev-parse B ) == $B_commit && echo branch B did not move
test $( git rev-parse @@{1} ) == $HEAD_commit && echo HEAD did move
test $( git branch --show-current ) == test && echo Current branch is test

test -f executable && echo executable is present
test -x executable && ( echo file 'executable' is executable after the rebase which is unexpected; ls -l; exit 1 )
test -f non-executable && echo non-executable is present
test -x non-executable || ( echo file 'non-executable' is not executable after the rebase which is unexpected; ls -l; exit 1 )
test -x final-executable-from-main || ( echo file 'final-executable-from-A' is not executable after the rebase which is unexpected; ls -l; exit 1 )
test -x final-executable-from-A || ( echo file 'final-executable-from-main' is not executable after the rebase which is unexpected; ls -l; exit 1 )


test -f separate-file.txt && echo separate-file.txt is present


# verifying contents of files

# let's verify the content of the file, just in case
cat > executable <<EOF
This is an executable file

Modifying the middle of the file in main... we will make it non-executable

Modifying the end of the file in A
EOF

cat > non-executable <<EOF
This is a non-executable file

Modifying the middle of the file in A... we will make it executable

Modifying the end of the file in main
EOF

test $( git status --short | wc -l ) -eq 0

get_chart
