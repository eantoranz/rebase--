# copyright (c) 2025 Edmundo Carmona Antoranz
# released under the terms of GPLv2.0

import pygit2
from pygit2.enums import FileMode

from rebasedashdash import merge_blobs_3way

from common import create_repository


def test_nochange_empty(tmp_path):
    repo = create_repository(tmp_path)

    assert merge_blobs_3way(repo, None, None, None) is None


def test_nochange_set(tmp_path):
    repo = create_repository(tmp_path)

    the_blob_id = repo.create_blob("Hello world")

    res = merge_blobs_3way(
        repo,
        (the_blob_id, FileMode.BLOB),
        (the_blob_id, FileMode.BLOB),
        (the_blob_id, FileMode.BLOB),
    )
    assert res == (the_blob_id, FileMode.BLOB)


def test_deleted(tmp_path):
    repo = create_repository(tmp_path)

    the_blob_id = repo.create_blob("Hello world")

    # deleted theirs
    res = merge_blobs_3way(
        repo, (the_blob_id, FileMode.BLOB), (the_blob_id, FileMode.BLOB), None
    )
    assert res is None

    # deleted ours
    res = merge_blobs_3way(
        repo, (the_blob_id, FileMode.BLOB), None, (the_blob_id, FileMode.BLOB)
    )
    assert res is None

    # deleted both
    res = merge_blobs_3way(repo, (the_blob_id, FileMode.BLOB), None, None)
    assert res is None


def test_added(tmp_path):
    repo = create_repository(tmp_path)

    the_blob_id = repo.create_blob("Hello world")

    # added ours
    res = merge_blobs_3way(repo, None, (the_blob_id, FileMode.BLOB), None)
    assert res == (the_blob_id, FileMode.BLOB)

    # added theirs
    res = merge_blobs_3way(repo, None, None, (the_blob_id, FileMode.BLOB))
    assert res == (the_blob_id, FileMode.BLOB)

    # added both
    res = merge_blobs_3way(
        repo, None, (the_blob_id, FileMode.BLOB), (the_blob_id, FileMode.BLOB)
    )
    assert res == (the_blob_id, FileMode.BLOB)


def test_changed_content(tmp_path):
    repo = create_repository(tmp_path)

    the_blob_id = repo.create_blob("Hello world")
    other_blob_id = repo.create_blob("Different content")

    # changed ours
    res = merge_blobs_3way(
        repo,
        (the_blob_id, FileMode.BLOB),
        (other_blob_id, FileMode.BLOB),
        (the_blob_id, FileMode.BLOB),
    )
    assert res == (other_blob_id, FileMode.BLOB)

    # changed theirs
    res = merge_blobs_3way(
        repo,
        (the_blob_id, FileMode.BLOB),
        (the_blob_id, FileMode.BLOB),
        (other_blob_id, FileMode.BLOB),
    )
    assert res == (other_blob_id, FileMode.BLOB)

    # changed both
    res = merge_blobs_3way(
        repo,
        (the_blob_id, FileMode.BLOB),
        (other_blob_id, FileMode.BLOB),
        (other_blob_id, FileMode.BLOB),
    )
    assert res == (other_blob_id, FileMode.BLOB)


def test_changed_filemode(tmp_path):
    repo = create_repository(tmp_path)

    the_blob_id = repo.create_blob("Hello world")

    # changed ours
    res = merge_blobs_3way(
        repo,
        (the_blob_id, FileMode.BLOB),
        (the_blob_id, FileMode.BLOB_EXECUTABLE),
        (the_blob_id, FileMode.BLOB),
    )
    assert res == (the_blob_id, FileMode.BLOB_EXECUTABLE)

    # changed theirs
    res = merge_blobs_3way(
        repo,
        (the_blob_id, FileMode.BLOB),
        (the_blob_id, FileMode.BLOB),
        (the_blob_id, FileMode.BLOB_EXECUTABLE),
    )
    assert res == (the_blob_id, FileMode.BLOB_EXECUTABLE)

    # changed both
    res = merge_blobs_3way(
        repo,
        (the_blob_id, FileMode.BLOB),
        (the_blob_id, FileMode.BLOB_EXECUTABLE),
        (the_blob_id, FileMode.BLOB_EXECUTABLE),
    )
    assert res == (the_blob_id, FileMode.BLOB_EXECUTABLE)


def test_change_content_and_filemode_together(tmp_path):
    repo = create_repository(tmp_path)

    the_blob_id = repo.create_blob("Hello world")
    other_blob_id = repo.create_blob("something different")

    # changed ours
    res = merge_blobs_3way(
        repo,
        (the_blob_id, FileMode.BLOB),
        (other_blob_id, FileMode.BLOB_EXECUTABLE),
        (the_blob_id, FileMode.BLOB),
    )
    assert res == (other_blob_id, FileMode.BLOB_EXECUTABLE)

    # changed theirs
    res = merge_blobs_3way(
        repo,
        (the_blob_id, FileMode.BLOB),
        (the_blob_id, FileMode.BLOB),
        (other_blob_id, FileMode.BLOB_EXECUTABLE),
    )
    assert res == (other_blob_id, FileMode.BLOB_EXECUTABLE)

    # changed both
    res = merge_blobs_3way(
        repo,
        (the_blob_id, FileMode.BLOB),
        (other_blob_id, FileMode.BLOB_EXECUTABLE),
        (other_blob_id, FileMode.BLOB_EXECUTABLE),
    )
    assert res == (other_blob_id, FileMode.BLOB_EXECUTABLE)


def test_change_content_and_filemode_separated(tmp_path):
    repo = create_repository(tmp_path)

    the_blob_id = repo.create_blob("Hello world")
    other_blob_id = repo.create_blob("something different")

    res = merge_blobs_3way(
        repo,
        (the_blob_id, FileMode.BLOB),
        (other_blob_id, FileMode.BLOB),
        (the_blob_id, FileMode.BLOB_EXECUTABLE),
    )
    assert res == (other_blob_id, FileMode.BLOB_EXECUTABLE)

    res = merge_blobs_3way(
        repo,
        (the_blob_id, FileMode.BLOB),
        (the_blob_id, FileMode.BLOB_EXECUTABLE),
        (other_blob_id, FileMode.BLOB),
    )
    assert res == (other_blob_id, FileMode.BLOB_EXECUTABLE)


def test_conflict_changed_content(tmp_path):
    repo = create_repository(tmp_path)

    ancestor_blob_id = repo.create_blob("ancestor")
    our_blob_id = repo.create_blob("ours")
    their_blob_id = repo.create_blob("theirs")

    res = merge_blobs_3way(
        repo,
        (ancestor_blob_id, FileMode.BLOB),
        (our_blob_id, FileMode.BLOB),
        (their_blob_id, FileMode.BLOB),
    )
    assert isinstance(res, pygit2.Index)
    assert res.conflicts is not None
    conflict = res.conflicts["a"]
    assert conflict[0] == pygit2.IndexEntry("a", ancestor_blob_id, FileMode.BLOB)
    assert conflict[1] == pygit2.IndexEntry("a", our_blob_id, FileMode.BLOB)
    assert conflict[2] == pygit2.IndexEntry("a", their_blob_id, FileMode.BLOB)


def test_conflict_changed_filemode(tmp_path):
    repo = create_repository(tmp_path)

    the_blob_id = repo.create_blob("ancestor")

    res = merge_blobs_3way(
        repo,
        (the_blob_id, FileMode.BLOB),
        (the_blob_id, FileMode.BLOB_EXECUTABLE),
        (the_blob_id, FileMode.LINK),
    )
    assert isinstance(res, pygit2.Index)
    assert res.conflicts is not None
    conflict = res.conflicts["a"]
    assert conflict[0] == pygit2.IndexEntry("a", the_blob_id, FileMode.BLOB)
    assert conflict[1] == pygit2.IndexEntry("a", the_blob_id, FileMode.BLOB_EXECUTABLE)
    assert conflict[2] == pygit2.IndexEntry("a", the_blob_id, FileMode.LINK)


def test_conflict_tree_conflict(tmp_path):
    repo = create_repository(tmp_path)

    ancestor_blob_id = repo.create_blob("ancestor")
    our_blob_id = repo.create_blob("ours")
    their_blob_id = repo.create_blob("theirs")

    # ours
    res = merge_blobs_3way(
        repo, (ancestor_blob_id, FileMode.BLOB), (our_blob_id, FileMode.BLOB), None
    )
    assert isinstance(res, pygit2.Index)
    assert res.conflicts is not None
    conflict = res.conflicts["a"]
    assert conflict[0] == pygit2.IndexEntry("a", ancestor_blob_id, FileMode.BLOB)
    assert conflict[1] == pygit2.IndexEntry("a", our_blob_id, FileMode.BLOB)
    assert conflict[2] is None

    res = merge_blobs_3way(
        repo, (ancestor_blob_id, FileMode.BLOB), None, (their_blob_id, FileMode.BLOB)
    )
    assert isinstance(res, pygit2.Index)
    assert res.conflicts is not None
    conflict = res.conflicts["a"]
    assert conflict[0] == pygit2.IndexEntry("a", ancestor_blob_id, FileMode.BLOB)
    assert conflict[1] is None
    assert conflict[2] == pygit2.IndexEntry("a", their_blob_id, FileMode.BLOB)
