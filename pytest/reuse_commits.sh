#!/bin/bash

# Test to reuse commits if possible

# will create a branch with 3 commits going over the same
# file on a few commits.

# the test will run the rebase on top of the first commit.
# That way we are forcing using the same original commits

. init_test.sh

cat > some-file.txt <<EOF
Content on the first commit
EOF
git add some-file.txt
git commit -m "first commit"

cat > some-file.txt <<EOF
Content on the second commit
EOF
git add some-file.txt
git commit -m "Second commit"

cat > some-file.txt <<EOF
Content on the third commit
EOF
git add some-file.txt
git commit -m "Third commit"

# If we run the rebase without a correct implementation to reuse the commits
# _and_ we are running within the same second that these commits for the test
# were generated, the IDs of the commits will still be the same and so the test
# would still pass which would be a false positive.
echo Sleeping for one second, sorry
sleep 1

get_chart
