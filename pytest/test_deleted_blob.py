# Copyright (c) 2025 Edmundo Carmona Antoranz
# Released under the terms of GPLv2

import copy
import pygit2

from rebasedashdash import RebaseOptions
from rebasedashdash import rebase

from common import add_test_blob
from common import add_test_tree
from common import create_commit
from common import create_repository
from common import create_test_tree
from common import get_tree_item
from common import remove_tree_item


def test_deleted_blob(tmp_path):
    repo = create_repository(tmp_path)

    main_tree = create_test_tree()
    test_dir = add_test_tree(main_tree, "test")
    file_to_delete_txt = 'Here is the content of the file in "main"'
    add_test_blob(
        test_dir, "file_to_delete.txt", pygit2.enums.FileMode.BLOB, file_to_delete_txt
    )
    another_txt = "Here is another file that won't be modified"
    add_test_blob(main_tree, "another.txt", pygit2.enums.FileMode.BLOB, another_txt)
    main_commits = [create_commit(repo, main_tree, "Setting up initial commit")]

    the_tree = repo.get(main_commits[-1]).tree
    assert len(the_tree) == 2
    the_directory = the_tree["test"]
    assert isinstance(the_directory, pygit2.Tree)
    assert len(the_directory) == 1
    assert the_tree["test/file_to_delete.txt"] is not None
    assert the_tree["another.txt"] is not None

    other_commits = copy.copy(main_commits)
    other_tree = copy.deepcopy(main_tree)

    # continue working on main
    file_to_delete_txt = 'Modifying the content of the file in "main"'
    add_test_blob(
        test_dir, "file_to_delete.txt", pygit2.enums.FileMode.BLOB, file_to_delete_txt
    )
    main_commits.append(
        create_commit(
            repo,
            main_tree,
            "Modifying the content of the file in main",
            main_commits[-1:],
        )
    )

    the_tree = repo.get(main_commits[-1]).tree
    assert len(the_tree) == 2
    the_directory = the_tree["test"]
    assert isinstance(the_directory, pygit2.Tree)
    assert len(the_directory) == 1
    assert the_tree["test/file_to_delete.txt"] is not None
    assert the_tree["another.txt"] is not None

    # we modify the file to be deleted in a different manner
    file_to_delete_txt = 'Modifying the content of the file in "other"'
    test_dir = get_tree_item(other_tree, "test")
    add_test_blob(
        test_dir, "file_to_delete.txt", pygit2.enums.FileMode.BLOB, file_to_delete_txt
    )
    other_commits.append(
        create_commit(
            repo,
            other_tree,
            "Modifying the content of the file in other",
            other_commits[-1:],
        )
    )

    the_tree = repo.get(other_commits[-1]).tree
    assert len(the_tree) == 2
    the_directory = the_tree["test"]
    assert isinstance(the_directory, pygit2.Tree)
    assert len(the_directory) == 1
    assert the_tree["test/file_to_delete.txt"] is not None
    assert the_tree["another.txt"] is not None

    # if we tried to merge, it should produce a conflict
    merge = repo.merge_commits(main_commits[-1], other_commits[-1])
    assert merge.conflicts is not None

    # let's do the merge in the air
    remove_tree_item(test_dir, "file_to_delete.txt")
    other_commits.append(
        create_commit(
            repo,
            other_tree,
            "Merging main into other",
            [other_commits[-1], main_commits[-1]],
        )
    )

    # verify the content of the merge commit
    the_tree = repo.get(other_commits[-1]).tree
    assert len(the_tree) == 1
    assert the_tree["another.txt"] is not None

    # continue working in main
    another_txt = "Ok, Ok... so I did modify it. Sue me!"
    add_test_blob(main_tree, "another.txt", pygit2.enums.FileMode.BLOB, another_txt)
    main_commits.append(
        create_commit(repo, main_tree, "Modifying the other file", main_commits[-1:])
    )

    the_tree = repo.get(main_commits[-1]).tree
    assert len(the_tree) == 2
    the_directory = the_tree["test"]
    assert isinstance(the_directory, pygit2.Tree)
    assert len(the_directory) == 1
    assert the_tree["test/file_to_delete.txt"] is not None
    assert the_tree["another.txt"] is not None

    file_to_delete_txt = (
        "By changing the content of the file, this should break the rebase\n"
        "as the file is not matching anymore the content of the file as it\n"
        "was defined in the first parent of the merge commit.\n"
    )
    test_dir = get_tree_item(main_tree, "test")
    add_test_blob(
        test_dir, "file_to_delete.txt", pygit2.enums.FileMode.BLOB, file_to_delete_txt
    )
    main_commits.append(
        create_commit(
            repo,
            main_tree,
            "Modifying the file that was deleted in the merge commit in other",
            main_commits[-1:],
        )
    )

    the_tree = repo.get(main_commits[-1]).tree
    assert len(the_tree) == 2
    the_directory = the_tree["test"]
    assert isinstance(the_directory, pygit2.Tree)
    assert len(the_directory) == 1
    assert the_tree["test/file_to_delete.txt"] is not None
    assert the_tree["another.txt"] is not None

    # setting up references
    repo.references.create("refs/heads/main", main_commits[-1])
    repo.references.create("refs/heads/other", other_commits[-1])

    main = repo.revparse_single("main")
    other = repo.revparse_single("other")
    assert all(
        item is not None and isinstance(item, pygit2.Commit) for item in [main, other]
    )

    conflicts = []
    rebase_options = RebaseOptions(main, other, main.parents[0])
    result = rebase(repo, rebase_options, conflicts)
    assert isinstance(result, pygit2.Commit)
    assert main.id != result.id
    assert other.id != result.id
    assert len(conflicts) == 0
    assert len(result.tree) == 1

    another = "Ok, Ok... so I did modify it. Sue me!"
    assert another == result.tree["another.txt"].data.decode()

    rebase_options = RebaseOptions(main, result)  # onto = main
    result2 = rebase(repo, rebase_options, conflicts)
    assert isinstance(result2, tuple)
    assert len(conflicts) == 1
