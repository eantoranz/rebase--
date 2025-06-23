# Copyright (c) 2025 Edmundo Carmona Antoranz
# Released under the terms of GPLv2.0

import copy
import pygit2

from rebasedashdash import rebase

from common import add_test_blob
from common import create_commit
from common import create_repository
from common import create_test_tree


def test_conflicting_blob_merge_commit_change_upstream(tmp_path):
    repo = create_repository(tmp_path)

    main_tree = create_test_tree()
    hello_world = (
        "1\n"
        "2\n"
        "3\n"
        "4\n"
        "5\n"
        "6\n"
        "7\n"
        "8\n"
        "9\n"
        "10\n"
        "11\n"
        "12\n"
        "13\n"
        "14\n"
        "15\n"
        "16\n"
        "17\n"
        "18\n"
        "19\n"
        "20\n"
    )
    add_test_blob(main_tree, "hello_world.txt", pygit2.enums.FileMode.BLOB, hello_world)
    commits_main = [create_commit(repo, main_tree, "hello world: numbers 1-20")]

    commits_A = copy.copy(commits_main)
    A_tree = copy.deepcopy(main_tree)
    commits_B = copy.copy(commits_main)
    B_tree = copy.deepcopy(main_tree)

    hello_world = (
        "1\n"
        "2\n"
        "3\n"
        "4\n"
        "5\n"
        "6\n"
        "27\n"
        "29\n"
        "10\n"
        "11\n"
        "12\n"
        "13\n"
        "14\n"
        "15\n"
        "16\n"
        "17\n"
        "18\n"
        "19\n"
        "20\n"
    )
    add_test_blob(main_tree, "hello_world.txt", pygit2.enums.FileMode.BLOB, hello_world)
    commits_main.append(
        create_commit(
            repo, main_tree, "hello world: 7=27, 8 is gone, 9=29", [commits_main[-1]]
        )
    )

    # switch to branch A
    hello_world = (
        "1\n"
        "2\n"
        "3\n"
        "4\n"
        "5\n"
        "6\n"
        "7\n"
        "8\n"
        "9\n"
        "10\n"
        "11\n"
        "12\n"
        "13\n"
        "14\n"
        "15\n"
        "37\n"
        "18\n"
        "19\n"
        "20\n"
    )
    add_test_blob(A_tree, "hello_world.txt", pygit2.enums.FileMode.BLOB, hello_world)
    commits_A.append(create_commit(repo, A_tree, "16 is gone, 17=37", [commits_A[-1]]))

    # clashing change in the file
    hello_world = (
        "1\n"
        "2\n"
        "3\n"
        "4\n"
        "5\n"
        "6\n"
        "27\n"
        "29\n"
        "10\n"
        "11\n"
        "12\n"
        "13\n"
        "14\n"
        "15\n"
        "16\n"
        "18\n"
        "19\n"
        "20\n"
    )
    add_test_blob(main_tree, "hello_world.txt", pygit2.enums.FileMode.BLOB, hello_world)
    commits_main.append(
        create_commit(repo, main_tree, "hello world: 17 is gone", [commits_main[-1]])
    )

    # if we try to merge it, there is a clash
    merge = repo.merge_commits(commits_main[-1], commits_A[-1])
    assert merge.conflicts is not None

    # let's ok ok... let's create the merge commit from thin air
    hello_world = (
        "1\n"
        "2\n"
        "3\n"
        "4\n"
        "5\n"
        "6\n"
        "27\n"
        "29\n"
        "10\n"
        "11\n"
        "12\n"
        "13\n"
        "14\n"
        "15\n"
        "16\n"
        "Something different\n"
        "18\n"
        "19\n"
        "20\n"
    )
    add_test_blob(main_tree, "hello_world.txt", pygit2.enums.FileMode.BLOB, hello_world)
    commits_main.append(
        create_commit(
            repo, main_tree, "merging branch A", [commits_main[-1], commits_A[-1]]
        )
    )

    # switch into B and add a non-conflicting change
    hello_world = (
        "1\n"
        "4\n"
        "5\n"
        "6\n"
        "7\n"
        "8\n"
        "9\n"
        "10\n"
        "11\n"
        "12\n"
        "13\n"
        "14\n"
        "15\n"
        "16\n"
        "17\n"
        "18\n"
        "19\n"
        "20\n"
    )
    add_test_blob(B_tree, "hello_world.txt", pygit2.enums.FileMode.BLOB, hello_world)
    commits_B.append(create_commit(repo, B_tree, "Removed 2 and 3", [commits_B[-1]]))

    repo.references.create("refs/heads/main", commits_main[-1])
    repo.references.create("refs/heads/A", commits_A[-1])
    repo.references.create("refs/heads/B", commits_B[-1])

    B = repo.revparse_single("B")
    main = repo.revparse_single("main")
    assert all(
        item is not None and isinstance(item, pygit2.Commit) for item in [main, B]
    )

    conflicts = []
    result = rebase(repo, B, main, B, conflicts)
    assert isinstance(result, pygit2.Commit)
    assert B.id != result.id
    assert main.id != result.id
    assert len(conflicts) == 0

    hello_world = (
        "1\n"
        "4\n"
        "5\n"
        "6\n"
        "27\n"
        "29\n"
        "10\n"
        "11\n"
        "12\n"
        "13\n"
        "14\n"
        "15\n"
        "16\n"
        "Something different\n"
        "18\n"
        "19\n"
        "20\n"
    )

    assert hello_world == result.tree["hello_world.txt"].data.decode()
