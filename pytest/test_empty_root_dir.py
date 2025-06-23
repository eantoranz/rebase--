# Copyright (c) 2025 Edmundo Carmona Antoranz
# Released under the terms of GPLv2.0

import copy
import pygit2

from rebasedashdash import rebase

from common import add_test_blob
from common import add_test_tree
from common import create_commit
from common import create_repository
from common import create_test_tree
from common import get_tree_item
from common import remove_tree_item


def test_empty_root_dir(tmp_path):
    repo = create_repository(tmp_path)

    main_tree = create_test_tree()
    a_dir_main = add_test_tree(main_tree, "a-dir")
    a_dir_A_txt = "content of file A"
    add_test_blob(a_dir_main, "A.txt", pygit2.enums.FileMode.BLOB, a_dir_A_txt)
    a_dir_B_txt = "content of file B"
    add_test_blob(a_dir_main, "B.txt", pygit2.enums.FileMode.BLOB, a_dir_B_txt)
    main_commits = [create_commit(repo, main_tree, "First commit with 2 files")]

    the_tree = repo.get(main_commits[-1]).tree
    assert len(the_tree) == 1
    the_directory = the_tree["a-dir"]
    assert isinstance(the_directory, pygit2.Tree)
    assert len(the_directory) == 2
    assert the_tree["a-dir/A.txt"] is not None
    assert the_tree["a-dir/B.txt"] is not None

    A_commits = copy.copy(main_commits)
    A_tree = copy.deepcopy(main_tree)

    B_commits = copy.copy(main_commits)
    B_tree = copy.deepcopy(main_tree)

    # going into the next commit
    # adding C.txt
    a_dir_C_txt = "Content of file c"
    add_test_blob(a_dir_main, "C.txt", pygit2.enums.FileMode.BLOB, a_dir_C_txt)
    main_commits.append(
        create_commit(repo, main_tree, "Adding C.txt", main_commits[-1:])
    )

    the_tree = repo.get(main_commits[-1]).tree
    assert len(the_tree) == 1
    the_directory = the_tree["a-dir"]
    assert isinstance(the_directory, pygit2.Tree)
    assert len(the_directory) == 3
    assert the_tree["a-dir/A.txt"] is not None
    assert the_tree["a-dir/B.txt"] is not None
    assert the_tree["a-dir/C.txt"] is not None

    # now we remove C.txt
    remove_tree_item(a_dir_main, "C.txt")
    main_commits.append(
        create_commit(repo, main_tree, "Removing C.txt", main_commits[-1:])
    )
    the_tree = repo.get(main_commits[-1]).tree
    assert len(the_tree) == 1
    the_directory = the_tree["a-dir"]
    assert isinstance(the_directory, pygit2.Tree)
    assert len(the_directory) == 2
    assert the_tree["a-dir/A.txt"] is not None
    assert the_tree["a-dir/B.txt"] is not None

    # on branch A we remove file B.txt
    remove_tree_item(get_tree_item(A_tree, "a-dir"), "A.txt")
    A_commits.append(create_commit(repo, A_tree, "Removing A.txt", A_commits[-1:]))
    the_tree = repo.get(A_commits[-1]).tree
    assert len(the_tree) == 1
    the_directory = the_tree["a-dir"]
    assert isinstance(the_directory, pygit2.Tree)
    assert len(the_directory) == 1
    assert the_tree["a-dir/B.txt"] is not None

    # on branch B we remove file B.txt
    remove_tree_item(get_tree_item(B_tree, "a-dir"), "B.txt")
    B_commits.append(create_commit(repo, B_tree, "Removing B.txt", B_commits[-1:]))
    the_tree = repo.get(B_commits[-1]).tree
    assert len(the_tree) == 1
    the_directory = the_tree["a-dir"]
    assert isinstance(the_directory, pygit2.Tree)
    assert len(the_directory) == 1
    assert the_tree["a-dir/A.txt"] is not None

    # a merge of A and B should succeed
    merge = repo.merge_commits(B_commits[-1], A_commits[-1])
    assert merge.conflicts is None

    # let's write this commit and set test over here
    test_commit = create_commit(
        repo, merge.write_tree(), "Merging A into test", [B_commits[-1], A_commits[-1]]
    )

    repo.references.create("refs/heads/test", test_commit)
    repo.references.create("refs/heads/A", A_commits[-1])
    repo.references.create("refs/heads/B", B_commits[-1])
    repo.references.create("refs/heads/main", main_commits[-1])

    main = repo.revparse_single("main")
    test = repo.revparse_single("test")
    assert all(
        item is not None and isinstance(item, pygit2.Commit) for item in [main, test]
    )

    conflicts = []
    result = rebase(repo, main.parents[0], test, main.parents[0], conflicts)
    assert isinstance(result, pygit2.Commit)
    assert main.parents[0].id != result.id
    assert test.id != result.id
    assert len(conflicts) == 0
    assert len(result.tree) == 1

    result2 = rebase(repo, main, result, main, conflicts)
    assert isinstance(result2, pygit2.Commit)
    assert main.parents[0].id != result2.id
    assert test.id != result2.id
    assert len(conflicts) == 0
    assert len(result2.tree) == 0
