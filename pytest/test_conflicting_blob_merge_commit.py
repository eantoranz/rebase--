# Copyright (c) 2025 Edmundo Carmona Antoranz
# Released under the terms of GPLv2.0

import copy
import pygit2

from rebasedashdash import rebase

from common import add_test_blob
from common import create_commit
from common import create_repository
from common import create_test_tree


def test_conflicting_blob_merge_commit(tmp_path):
    repo = create_repository(tmp_path)

    main_tree = create_test_tree()
    hello_world = (
        "Hello world\n"
        "\n"
        "This is the initial commit of the file\n"
        "\n"
        "Wrapping up the file\n"
    )
    add_test_blob(main_tree, "hello_world.txt", pygit2.enums.FileMode.BLOB, hello_world)
    main_commits = [create_commit(repo, main_tree, "hello world: initial commit")]

    A_commits = copy.copy(main_commits)
    A_tree = copy.deepcopy(main_tree)

    B_commits = copy.copy(main_commits)
    B_tree = copy.deepcopy(main_tree)

    hello_world = (
        "Hello world\n"
        "\n"
        "We are modifying the middle of the file\n"
        "\n"
        "Wrapping up the file\n"
    )
    add_test_blob(main_tree, "hello_world.txt", pygit2.enums.FileMode.BLOB, hello_world)
    main_commits.append(
        create_commit(
            repo,
            main_tree,
            "hello world: modifying the middle of the file",
            main_commits,
        )
    )

    # work on A
    hello_world = (
        "Hello world\n"
        "\n"
        "A different content from what we have setup in main\n"
        "\n"
        "Wrapping up the file\n"
    )
    add_test_blob(A_tree, "hello_world.txt", pygit2.enums.FileMode.BLOB, hello_world)
    A_commits.append(
        create_commit(
            repo, A_tree, "hello world: also modified the middle of the file", A_commits
        )
    )

    # normal merge of A into main
    merge = repo.merge_commits(main_commits[-1], A_commits[-1])
    assert merge.conflicts is not None

    # let's create the merge out of thin air
    hello_world = (
        "Hello world\n"
        "\n"
        "This is how we solved the conflict\n"
        "\n"
        "Wrapping up the file\n"
    )
    add_test_blob(main_tree, "hello_world.txt", pygit2.enums.FileMode.BLOB, hello_world)
    main_commits.append(
        create_commit(
            repo,
            main_tree,
            "merging branch A into main",
            [main_commits[-1], A_commits[-1]],
        )
    )

    # add a completely different file in B
    separate_file = "this is a separate file"
    add_test_blob(
        B_tree, "separate-file.txt", pygit2.enums.FileMode.BLOB, separate_file
    )
    B_commits.append(
        create_commit(repo, B_tree, "merging branch A into main", B_commits)
    )

    # now we setup the references
    repo.references.create("refs/heads/A", A_commits[-1])
    repo.references.create("refs/heads/B", B_commits[-1])
    repo.references.create("refs/heads/main", main_commits[-1])
    repo.references.create("refs/heads/test", main_commits[-1])

    # the test itself
    test = repo.revparse_single("test")
    B = repo.revparse_single("B")
    assert all(
        item is not None and isinstance(item, pygit2.Commit) for item in [test, B]
    )

    conflicts = []
    result = rebase(repo, B, test, B, conflicts)
    assert isinstance(result, pygit2.Commit)
    assert B.id != result.id
    assert test.id != result.id
    assert len(conflicts) == 0

    separate_file = "this is a separate file"
    hello_world = (
        "Hello world\n"
        "\n"
        "This is how we solved the conflict\n"
        "\n"
        "Wrapping up the file\n"
    )

    assert separate_file == result.tree["separate-file.txt"].data.decode()
    assert hello_world == result.tree["hello_world.txt"].data.decode()
