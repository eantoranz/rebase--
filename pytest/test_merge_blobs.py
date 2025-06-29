# copyright (c) 2025 Edmundo Carmona Antoranz
# released under the terms of GPLv2.0

import pygit2
from pygit2.enums import FileMode

from rebasedashdash import CommitMetadata
from rebasedashdash import merge_blobs

from common import add_test_blob
from common import create_blob
from common import create_commit
from common import create_repository
from common import create_test_tree


def test_merge_blobs_ancestor_no_change_differing_parent(tmp_path):
    # there will be a single differing parent.
    # the file will be different from the differing parent.
    # However, the original differing parent blob will match
    # the content of the common ancestor of the parents
    # of the original commit. If there is more than one parent in
    # the commit, that means that the content of the original
    # commit can be taken as is

    repo = create_repository(tmp_path)

    # let's create a merge commit that has a content of a a_file
    # that matches the content of the merge_base of the parents of the original commit

    root_tree = create_test_tree()
    add_test_blob(root_tree, "a_file", pygit2.enums.FileMode.BLOB, "blob2")
    main_commit_ids = [create_commit(repo, root_tree, "setting up common ancestor")]

    root_tree = create_test_tree()
    add_test_blob(
        root_tree, "a_file", pygit2.enums.FileMode.BLOB, "one side of the merge"
    )
    main_commit_ids.append(
        create_commit(
            repo, root_tree, "setting up one side of the merge", main_commit_ids
        )
    )

    # the other side of the merge
    root_tree = create_test_tree()
    add_test_blob(
        root_tree, "a_file", pygit2.enums.FileMode.BLOB, "other side of the merge"
    )
    other_commit_id = create_commit(
        repo, root_tree, "setting up the other side of the merge", main_commit_ids[:1]
    )  # only the first commit

    root_tree = create_test_tree()
    add_test_blob(
        root_tree, "a_file", pygit2.enums.FileMode.BLOB, "result of the merge"
    )
    main_commit_ids.append(
        create_commit(
            repo, root_tree, "merging", [main_commit_ids[-1], other_commit_id]
        )
    )

    main_tip = repo.get(main_commit_ids[-1])

    assert (
        repo.merge_base(main_tip.parents[0].id, main_tip.parents[1].id)
        == main_commit_ids[0]
    )  # make sure the merge base is correct

    # need to create a separate commit tree that has 2 tips (like the rebased merge commit we are trying to rebase)
    # and in the common ancestor content is like blob3
    # common ancestor
    root_tree = create_test_tree()
    add_test_blob(root_tree, "a_file", pygit2.enums.FileMode.BLOB, "blob3")
    rebased_commit_ids1 = [
        create_commit(repo, root_tree, "setting up rebased common ancestor")
    ]

    # this side won't be changed
    root_tree = create_test_tree()
    rebased_commit_ids1.append(
        create_commit(repo, root_tree, "this side does not change", rebased_commit_ids1)
    )

    # this should be enough to get the common ancestor

    blob1 = create_blob(repo, "a_file", "blob1", pygit2.enums.FileMode.BLOB)
    blob2 = create_blob(repo, "a_file", "blob2", pygit2.enums.FileMode.BLOB)
    blob3 = create_blob(repo, "a_file", "blob3", pygit2.enums.FileMode.BLOB)

    metadata = CommitMetadata(
        repo, main_tip, [repo.get(id) for id in rebased_commit_ids1]
    )  # using

    res = merge_blobs(metadata, "a_file", blob1, [blob2], [blob3])
    assert isinstance(res, tuple)
