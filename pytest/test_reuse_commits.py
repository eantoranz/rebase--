# Copyright (c) 2025 Edmundo Carmona Antoranz
# Released under the terms of GPLv2.0

import pygit2
import time

from rebasedashdash import rebase

from common import add_test_blob
from common import create_commit
from common import create_repository
from common import create_test_tree


def test_reuse_commits(tmp_path):
    # * CCCC third commit (main)
    # * BBBB second commit
    # * AAAA first commit
    #
    # running a rebase AAAA main --onto AAAA should reuse AAAA..main commits
    repo = create_repository(tmp_path)

    root_tree = create_test_tree()
    add_test_blob(
        root_tree,
        "some-file.txt",
        pygit2.enums.FileMode.BLOB,
        "Content on the first commit",
    )
    commit_id = create_commit(repo, root_tree, "first commit", [])
    commit_ids = [commit_id]

    root_tree = create_test_tree()
    add_test_blob(
        root_tree,
        "some-file.txt",
        pygit2.enums.FileMode.BLOB,
        "Content on the second commit",
    )
    commit_id = create_commit(repo, root_tree, "second commit", [commit_ids[-1]])
    commit_ids.append(commit_id)

    root_tree = create_test_tree()
    add_test_blob(
        root_tree,
        "some-file.txt",
        pygit2.enums.FileMode.BLOB,
        "Content on the third commit",
    )
    commit_id = create_commit(repo, root_tree, "third commit", [commit_ids[-1]])
    commit_ids.append(commit_id)

    # we allow 1 second to go so that IDs are not _forced_ to be the same if
    # the implementation to reuse commits is broken
    time.sleep(1)

    # not really using references _yet_
    main = repo.get(commit_ids[-1])
    base = repo.get(commit_ids[0])
    assert all(
        item is not None and isinstance(item, pygit2.Commit) for item in [main, base]
    )

    conflicts = []
    result = rebase(repo, base, main, base, conflicts)
    assert isinstance(result, pygit2.Commit)
    assert main.id == result.id
