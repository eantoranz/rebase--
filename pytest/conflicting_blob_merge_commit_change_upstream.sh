#!/bin/bash

# Rebasing a merge commit where a file
# got a conflict.
#
# There is also a change made in upstream
# that is is not related to the section
# involved in the conflict

. init_test.sh

cat > hello_world.txt <<EOF
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
EOF

git add hello_world.txt
git commit -m "hello world: numbers 1-20"

git branch A
git branch B

cat > hello_world.txt <<EOF
1
2
3
4
5
6
27
29
10
11
12
13
14
15
16
17
18
19
20
EOF

git add hello_world.txt
git commit -m "hello world: 7=27, 8 is gone, 9=29"

git switch A
git branch 

cat > hello_world.txt <<EOF
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
37
18
19
20
EOF

git add hello_world.txt
git commit -m "16 is gone, 17=37"

git checkout main

# We add a clashing change in the file
cat > hello_world.txt <<EOF
1
2
3
4
5
6
27
29
10
11
12
13
14
15
16
18
19
20
EOF

git commit -m "hello-world: 17 is gone" hello_world.txt

# now we merge, it should not fail
git merge -m "merging branch A" A || echo There is a conflict when merging, totally expected it

test $( git status --short | wc -l ) -ne 0 || ( echo Status is clean which is not expected; git status; exit 1 )

# let's solve the conflict
cat > hello_world.txt <<EOF
1
2
3
4
5
6
27
29
10
11
12
13
14
15
16
Something different
18
19
20
EOF

git add hello_world.txt
git merge --continue

git switch B

# add a change that does not mess with the conflicting part from the other branch
cat > hello_world.txt <<EOF
1
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
EOF


git add hello_world.txt
git commit -m "Removed 2 and 3"

get_chart