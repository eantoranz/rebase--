# copyright (c) 2025 Edmundo Carmona Antoranz
# released under the terms of GPLv2.0

import pygit2
from pygit2.enums import FileMode

from rebasedashdash import merge_blobs

from common import create_repository
from common import create_blob


## single parent tests
def test_single_parent_no_change(tmp_path):
    repo = create_repository(tmp_path)

    parent_blob = create_blob(repo, "testfile.txt", "Content of the parent")

    child_blob = create_blob(repo, "testfile.txt", "Content of the child")

    orig_blob = create_blob(repo, "testfile.txt", "Content of the final result")

    res = merge_blobs(
        repo, orig_blob, parent_blob, [child_blob], parent_blob, [child_blob], True
    )

    assert res == (orig_blob.id, FileMode.BLOB)


def test_single_parent_change_between_bases(tmp_path):
    repo = create_repository(tmp_path)

    old_merge_base_blob = create_blob(
        repo,
        "testfile.txt",
        "Original merge base content\n"
        "\n"
        "This line will be changed in the parents\n"
        "\n"
        "Closing of the file\n",
    )

    old_parent_blob = create_blob(
        repo,
        "testfile.txt",
        "Original merge base content\n"
        "\n"
        "This is the content on a parent\n"
        "\n"
        "Closing of the file\n",
    )

    new_merge_base_blob = create_blob(
        repo,
        "testfile.txt",
        "New merge base content\n"
        "\n"
        "This line will be changed in the parents\n"
        "\n"
        "Closing of the file\n",
    )

    new_parent_blob = create_blob(
        repo,
        "testfile.txt",
        "New merge base content\n"
        "\n"
        "This is the content on a parent\n"
        "\n"
        "Closing of the file\n",
    )

    orig_blob = create_blob(
        repo,
        "testfile.txt",
        "Original merge base content\n"
        "\n"
        "This is the content on a parent\n"
        "\n"
        "Closing of the file\n",
    )

    expected_blob = create_blob(
        repo,
        "testfile.txt",
        "New merge base content\n"
        "\n"
        "This is the content on a parent\n"
        "\n"
        "Closing of the file\n",
    )

    res = merge_blobs(
        repo,
        orig_blob,
        old_merge_base_blob,
        [old_parent_blob],
        new_merge_base_blob,
        [new_parent_blob],
        True,
    )

    assert res == (expected_blob.id, FileMode.BLOB)


def test_single_parent_change_between_parents(tmp_path):
    repo = create_repository(tmp_path)

    merge_base_blob = create_blob(
        repo,
        "testfile.txt",
        "Original merge base content\n"
        "\n"
        "This is the content on the merge base\n"
        "\n"
        "Closing of the file\n",
    )

    parent_blob = create_blob(
        repo,
        "testfile.txt",
        "Original merge base content\n"
        "\n"
        "This is the content on the original parent\n"
        "\n"
        "Closing of the file\n",
    )

    rebased_parent_blob = create_blob(
        repo,
        "testfile.txt",
        "Original merge base content\n"
        "\n"
        "This is the content on the rebased parent\n"
        "\n"
        "Closing of the file\n",
    )

    orig_blob = create_blob(
        repo,
        "testfile.txt",
        "Original merge base content\n"
        "\n"
        "This is the content on the original parent\n"
        "\n"
        "Closing of the file\n",
    )

    expected_blob = create_blob(
        repo,
        "testfile.txt",
        "Original merge base content\n"
        "\n"
        "This is the content on the rebased parent\n"
        "\n"
        "Closing of the file\n",
    )

    res = merge_blobs(
        repo,
        orig_blob,
        merge_base_blob,
        [parent_blob],
        merge_base_blob,
        [rebased_parent_blob],
        True,
    )

    assert res == (expected_blob.id, FileMode.BLOB)


def test_single_parent_change_between_bases_and_parents(tmp_path):
    repo = create_repository(tmp_path)

    merge_base_blob = create_blob(
        repo,
        "testfile.txt",
        "Original merge base content\n"
        "\n"
        "This is the content on the merge base\n"
        "\n"
        "Closing of the file\n",
    )

    parent_blob = create_blob(
        repo,
        "testfile.txt",
        "Original merge base content\n"
        "\n"
        "This is the content on the original parent\n"
        "\n"
        "Closing of the file\n",
    )

    orig_blob = create_blob(
        repo,
        "testfile.txt",
        "Original merge base content\n"
        "\n"
        "This is the content on the original parent\n"
        "\n"
        "Closing of the file\n",
    )

    rebased_merge_base_blob = create_blob(
        repo,
        "testfile.txt",
        "Modified merge base content\n"
        "\n"
        "This is the content on the merge base\n"
        "\n"
        "Closing of the file\n",
    )

    rebased_parent_blob = create_blob(
        repo,
        "testfile.txt",
        "Modified merge base content\n"
        "\n"
        "This is the content on the rebased parent\n"
        "\n"
        "Closing of the file\n",
    )

    expected_blob = create_blob(
        repo,
        "testfile.txt",
        "Modified merge base content\n"
        "\n"
        "This is the content on the rebased parent\n"
        "\n"
        "Closing of the file\n",
    )

    res = merge_blobs(
        repo,
        orig_blob,
        merge_base_blob,
        [parent_blob],
        rebased_merge_base_blob,
        [rebased_parent_blob],
        True,
    )

    assert res == (expected_blob.id, FileMode.BLOB)


## multiple parent tests
def test_multiple_parents_no_change(tmp_path):
    repo = create_repository(tmp_path)

    merge_base_blob = create_blob(repo, "testfile.txt", "Content of the merge base")

    parent_blob1 = create_blob(repo, "testfile.txt", "Content of the first parent")

    parent_blob2 = create_blob(repo, "testfile.txt", "Content of the second parent")

    orig_blob = create_blob(repo, "testfile.txt", "Content of the final result")

    res = merge_blobs(
        repo,
        orig_blob,
        merge_base_blob,
        [parent_blob1, parent_blob2],
        merge_base_blob,
        [parent_blob1, parent_blob2],
        True,
    )

    assert res == (orig_blob.id, FileMode.BLOB)


def test_multiple_parents_change_between_bases(tmp_path):
    repo = create_repository(tmp_path)

    old_merge_base_blob = create_blob(
        repo,
        "testfile.txt",
        "Original merge base content\n"
        "\n"
        "This line will be changed in the parents\n"
        "\n"
        "Closing of the file\n",
    )

    old_parent_blob1 = create_blob(
        repo,
        "testfile.txt",
        "Original merge base content\n"
        "\n"
        "This is the content on parent 1\n"
        "\n"
        "Closing of the file\n",
    )

    old_parent_blob2 = create_blob(
        repo,
        "testfile.txt",
        "Original merge base content\n"
        "\n"
        "This is the content on parent 2\n"
        "\n"
        "Closing of the file\n",
    )

    new_merge_base_blob = create_blob(
        repo,
        "testfile.txt",
        "New merge base content\n"
        "\n"
        "This line will be changed in the parents\n"
        "\n"
        "Closing of the file\n",
    )

    new_parent_blob1 = create_blob(
        repo,
        "testfile.txt",
        "New merge base content\n"
        "\n"
        "This is the content on parent 1\n"
        "\n"
        "Closing of the file\n",
    )

    new_parent_blob2 = create_blob(
        repo,
        "testfile.txt",
        "New merge base content\n"
        "\n"
        "This is the content on parent 2\n"
        "\n"
        "Closing of the file\n",
    )

    orig_blob = create_blob(
        repo,
        "testfile.txt",
        "Original merge base content\n"
        "\n"
        "This is the result of the merge\n"
        "\n"
        "Closing of the file\n",
    )

    expected_blob = create_blob(
        repo,
        "testfile.txt",
        "New merge base content\n"
        "\n"
        "This is the result of the merge\n"
        "\n"
        "Closing of the file\n",
    )

    res = merge_blobs(
        repo,
        orig_blob,
        old_merge_base_blob,
        [old_parent_blob1, old_parent_blob2],
        new_merge_base_blob,
        [new_parent_blob1, new_parent_blob2],
        True,
    )

    assert res == (expected_blob.id, FileMode.BLOB)


def test_multiple_parents_change_between_parents(tmp_path):
    repo = create_repository(tmp_path)

    merge_base_blob = create_blob(
        repo,
        "testfile.txt",
        "Original merge base content\n"
        "\n"
        "This is a line that will me modified on both parents of the merge commit\n"
        "\n"
        "This line will be modified between parent 1's\n"
        "\n"
        "This line will be modified between parent 2's\n"
        "\n"
        "Closing of the file\n",
    )

    parent_blob1 = create_blob(
        repo,
        "testfile.txt",
        "Original merge base content\n"
        "\n"
        "This is the way this line is written on parent 1\n"
        "\n"
        "This line will be modified between parent 1's\n"
        "\n"
        "This line will be modified between parent 2's\n"
        "\n"
        "Closing of the file\n",
    )

    parent_blob2 = create_blob(
        repo,
        "testfile.txt",
        "Original merge base content\n"
        "\n"
        "This is the way this line is written on parent 2\n"
        "\n"
        "This line will be modified between parent 1's\n"
        "\n"
        "This line will be modified between parent 2's\n"
        "\n"
        "Closing of the file\n",
    )

    orig_blob = create_blob(
        repo,
        "testfile.txt",
        "Original merge base content\n"
        "\n"
        "This is the way this line is written on the merge commit\n"
        "\n"
        "This line will be modified between parent 1's\n"
        "\n"
        "This line will be modified between parent 2's\n"
        "\n"
        "Closing of the file\n",
    )

    rebased_parent_blob1 = create_blob(
        repo,
        "testfile.txt",
        "Original merge base content\n"
        "\n"
        "This is the way this line is written on parent 1\n"
        "\n"
        "This line has been modified between parent 1's\n"
        "\n"
        "This line will be modified between parent 2's\n"
        "\n"
        "Closing of the file\n",
    )

    rebased_parent_blob2 = create_blob(
        repo,
        "testfile.txt",
        "Original merge base content\n"
        "\n"
        "This is the way this line is written on parent 2\n"
        "\n"
        "This line will be modified between parent 1's\n"
        "\n"
        "This line has been modified between parent 2's\n"
        "\n"
        "Closing of the file\n",
    )

    expected_blob = create_blob(
        repo,
        "testfile.txt",
        "Original merge base content\n"
        "\n"
        "This is the way this line is written on the merge commit\n"
        "\n"
        "This line has been modified between parent 1's\n"
        "\n"
        "This line has been modified between parent 2's\n"
        "\n"
        "Closing of the file\n",
    )

    res = merge_blobs(
        repo,
        orig_blob,
        merge_base_blob,
        [parent_blob1, parent_blob2],
        merge_base_blob,
        [rebased_parent_blob1, rebased_parent_blob2],
        True,
    )

    assert res == (expected_blob.id, FileMode.BLOB)


def test_multiple_parents_change_between_bases_and_parents(tmp_path):
    repo = create_repository(tmp_path)

    merge_base_blob = create_blob(
        repo,
        "testfile.txt",
        "Original merge base content\n"
        "\n"
        "This is a line that will me modified on both parents of the merge commit\n"
        "\n"
        "This line will be modified between parent 1's\n"
        "\n"
        "This line will be modified between parent 2's\n"
        "\n"
        "Closing of the file\n",
    )

    parent_blob1 = create_blob(
        repo,
        "testfile.txt",
        "Original merge base content\n"
        "\n"
        "This is the way this line is written on parent 1\n"
        "\n"
        "This line will be modified between parent 1's\n"
        "\n"
        "This line will be modified between parent 2's\n"
        "\n"
        "Closing of the file\n",
    )

    parent_blob2 = create_blob(
        repo,
        "testfile.txt",
        "Original merge base content\n"
        "\n"
        "This is the way this line is written on parent 2\n"
        "\n"
        "This line will be modified between parent 1's\n"
        "\n"
        "This line will be modified between parent 2's\n"
        "\n"
        "Closing of the file\n",
    )

    orig_blob = create_blob(
        repo,
        "testfile.txt",
        "Original merge base content\n"
        "\n"
        "This is the way this line is written on the merge commit\n"
        "\n"
        "This line will be modified between parent 1's\n"
        "\n"
        "This line will be modified between parent 2's\n"
        "\n"
        "Closing of the file\n",
    )

    rebased_merge_base_blob = create_blob(
        repo,
        "testfile.txt",
        "Rebased merge base content\n"
        "\n"
        "This is a line that will me modified on both parents of the merge commit\n"
        "\n"
        "This line will be modified between parent 1's\n"
        "\n"
        "This line will be modified between parent 2's\n"
        "\n"
        "Closing of the file\n",
    )

    rebased_parent_blob1 = create_blob(
        repo,
        "testfile.txt",
        "Rebased merge base content\n"
        "\n"
        "This is the way this line is written on parent 1\n"
        "\n"
        "This line has been modified between parent 1's\n"
        "\n"
        "This line will be modified between parent 2's\n"
        "\n"
        "Closing of the file\n",
    )

    rebased_parent_blob2 = create_blob(
        repo,
        "testfile.txt",
        "Rebased merge base content\n"
        "\n"
        "This is the way this line is written on parent 2\n"
        "\n"
        "This line will be modified between parent 1's\n"
        "\n"
        "This line has been modified between parent 2's\n"
        "\n"
        "Closing of the file\n",
    )

    expected_blob = create_blob(
        repo,
        "testfile.txt",
        "Rebased merge base content\n"
        "\n"
        "This is the way this line is written on the merge commit\n"
        "\n"
        "This line has been modified between parent 1's\n"
        "\n"
        "This line has been modified between parent 2's\n"
        "\n"
        "Closing of the file\n",
    )

    res = merge_blobs(
        repo,
        orig_blob,
        merge_base_blob,
        [parent_blob1, parent_blob2],
        rebased_merge_base_blob,
        [rebased_parent_blob1, rebased_parent_blob2],
        True,
    )

    assert res == (expected_blob.id, FileMode.BLOB)
