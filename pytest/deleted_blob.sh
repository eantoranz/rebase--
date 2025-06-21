#!/bin/bash

# Deleting a blob in a merge
#
# It should be fine as long as the file is nor modified in upstream

. init_test.sh

mkdir test

cat > test/file_to_delete.txt <<EOF
Here is the content of the file in "main"
EOF

cat > another.txt <<EOF
Here is another file that won't be modified
EOF

git add test/file_to_delete.txt another.txt
git commit -m "Setting up initial commit"

git branch other

cat > test/file_to_delete.txt <<EOF
Modifying the content of the file in "main"
EOF

git commit -m "Modifying the content of the file in main" test/

git switch other

cat > test/file_to_delete.txt <<EOF
Modifying the content of the file in "other"
EOF

git commit -m "Modifying the content of the file in other" test/

# let's merge into "other", we should get a conflict

git merge -m "Merging main into other" main || ( echo there was a conflict, as expected )
test $( git status --short | wc -l ) -ne 0 || ( echo Status is clean which is unexpected; git status; exit 1 )

# let's delete the file as a result
git rm test/file_to_delete.txt

git merge --continue

git switch main

# let's _not_ modify the deleted file
cat > another.txt <<EOF
Ok, Ok... so I did modify it. Sue me!
EOF

git commit -m "Modifying the other file" another.txt

cat > test/file_to_delete.txt <<EOF
By changing the content of the file, this should break the rebase
as the file is not matching anymore the content of the file as it
was defined in the first parent of the merge commit.
EOF

git commit -m "Modifying the file that was deleted in the merge commit in A" test/

get_chart