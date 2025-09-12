# Copyright (c) 2025 Edmundo Carmona Antoranz
# Released under the terms of GPLv2.0

import pygit2

from rebasedashdash import RebaseOptions
from rebasedashdash import rebase

from common import add_test_blob
from common import create_commit
from common import create_repository
from common import create_test_tree


"""
Sequence of git commands to replicate this scenario

git init .
git checkout -b main
cat > hello_world.txt <<EOF
Hello world

This is the initial commit of the file

Wrapping up the file
EOF
git add hello_world.txt
git commit -m "hello world: initial commit"

# create branch other
git branch other

# second commit in main
cat > hello_world.txt <<EOF
Hello world

We are modifying the middle of the file

Wrapping up the file
EOF
git add hello_world.txt
git commit -m "hello world: modifying the middle of the file"

# second commit in other
cat > hello_world.txt <<EOF
Hello world

This is the initial commit of the file

We are modifying the end of the file
EOF
git add hello_world.txt
git commit -m "hello world: modifying the end of the file"

# now we run the rebase
git rebase main other
"""


def test_simple_rebase(tmp_path):
    # * CCCC (main)
    # | * BBBB (other)
    # |/
    # * AAAA
    #
    # rebase other on top of main
    repo = create_repository(tmp_path)

    hello_world = (
        "Hello world\n"
        "\n"
        "This is the initial commit of the file\n"
        "\n"
        "Wrapping up the file\n"
    )
    root_tree = create_test_tree()
    add_test_blob(root_tree, "hello_world.txt", pygit2.enums.FileMode.BLOB, hello_world)
    main_commit_ids = [create_commit(repo, root_tree, "hello world: initial commit")]

    hello_world = (
        "Hello world\n"
        "\n"
        "We are modifying the middle of the file\n"
        "\n"
        "Wrapping up the file\n"
    )
    root_tree = create_test_tree()
    add_test_blob(root_tree, "hello_world.txt", pygit2.enums.FileMode.BLOB, hello_world)
    main_commit_ids.append(
        create_commit(
            repo,
            root_tree,
            "hello world: modifying the middle of the file",
            main_commit_ids,
        )
    )

    repo.references.create("refs/heads/main", main_commit_ids[-1])

    # starting to work on other
    other_commits_ids = main_commit_ids[0:1]
    hello_world = (
        "Hello world\n"
        "\n"
        "This is the initial commit of the file\n"
        "\n"
        "We are modifying the end of the file\n"
    )
    root_tree = create_test_tree()
    add_test_blob(root_tree, "hello_world.txt", pygit2.enums.FileMode.BLOB, hello_world)
    other_commit_ids = [
        create_commit(
            repo,
            root_tree,
            "hello world: modifying the end of the file",
            other_commits_ids,
        )
    ]

    repo.references.create("refs/heads/other", other_commit_ids[-1])

    # let's run a rebase
    main = repo.revparse_single("main")
    other = repo.revparse_single("other")
    assert all(
        item is not None and isinstance(item, pygit2.Commit) for item in [main, other]
    )

    conflicts = []
    rebase_options = RebaseOptions(main, other)  # onto is main
    rebase_options.debug = True
    result = rebase(repo, rebase_options, conflicts)
    assert isinstance(result, pygit2.Commit)
    assert main.id != result.id
    assert other.id != result.id
    assert len(conflicts) == 0

    hello_world = (
        "Hello world\n"
        "\n"
        "We are modifying the middle of the file\n"
        "\n"
        "We are modifying the end of the file\n"
    )

    assert hello_world == result.tree["hello_world.txt"].data.decode()
