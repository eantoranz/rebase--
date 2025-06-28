# copyright (c) 2025 Edmundo Carmona Antoranz
# released under the terms of GPLv2.0

from pygit2.enums import FileMode

from rebasedashdash import easy_merge

from common import create_repository

# easy_merge(commit_item, original_item, rebased_item)


def test_all_empty():

    assert easy_merge(None, None, None) == (True, None)


def test_all_same(tmp_path):
    repo = create_repository(tmp_path)

    blob_id = repo.create_blob("hello world")

    tree_builder = repo.TreeBuilder()
    tree_builder.insert("file1", blob_id, FileMode.BLOB)
    tree = repo.get(tree_builder.write())

    blob = tree["file1"]

    assert easy_merge(blob, blob, blob) == (True, blob)


def test_blob_same_content_different_name(tmp_path):
    repo = create_repository(tmp_path)

    blob_id = repo.create_blob("hello world")

    tree_builder = repo.TreeBuilder()
    tree_builder.insert("file1", blob_id, FileMode.BLOB)
    tree_builder.insert("file2", blob_id, FileMode.BLOB)
    tree = repo.get(tree_builder.write())

    blob1 = tree["file1"]
    blob2 = tree["file2"]

    solved, res_blob = easy_merge(blob1, blob1, blob2)
    # rebased item is different, no change between original item and commit item
    # => take rebased item
    assert solved
    assert res_blob.name == blob2.name
    assert res_blob.id == blob2.id
    assert res_blob.filemode == blob2.filemode

    solved, res_blob = easy_merge(blob1, blob2, blob1)
    # commit item is the same as rebased item, original item is different
    # => change is already applied, take commit item (or rebased item)
    assert solved
    assert res_blob.name == blob1.name
    assert res_blob.id == blob1.id
    assert res_blob.filemode == blob1.filemode

    solved, res_blob = easy_merge(blob1, blob2, blob2)
    # rebased and original item are the same, commit item is different
    # => take commit item
    assert solved
    assert res_blob.name == blob1.name
    assert res_blob.id == blob1.id
    assert res_blob.filemode == blob1.filemode


def blobs_different_names(tmp_path):
    repo = create_repository(tmp_path)

    hello_id = repo.create_blob("hello world")
    buh_bye_id = repo.create_blob("buh bye")

    tree_builder = repo.TreeBuilder()
    tree_builder.insert("commit", hello_id, FileMode.BLOB)
    tree_builder.insert("original", hello_id, FileMode.BLOB)
    tree_builder.insert("rebased", buh_bye_id, FileMode.BLOB)
    tree = repo.get(tree_builder.write())

    commit_item = tree["commit"]
    original_item = tree["original"]
    rebased_item = tree["original"]

    solved, res_item = easy_merge(commit_item, original_item, rebased_item)
    assert not solved
    assert res_item is None


def test_deleted_both_ways(tmp_path):
    repo = create_repository(tmp_path)

    hello_id = repo.create_blob("hello world")

    tree_builder = repo.TreeBuilder()
    tree_builder.insert("original", hello_id, FileMode.BLOB)
    tree = repo.get(tree_builder.write())

    original_item = tree["original"]

    solved, res_item = easy_merge(None, original_item, None)
    assert solved
    assert res_item is None


def test_no_original_same_commit_and_rebased(tmp_path):
    repo = create_repository(tmp_path)

    hello_id = repo.create_blob("hello world")

    tree_builder = repo.TreeBuilder()
    tree_builder.insert("one_file", hello_id, FileMode.BLOB)
    tree = repo.get(tree_builder.write())

    one_file = tree["one_file"]

    solved, res_item = easy_merge(one_file, None, one_file)
    assert solved
    assert (res_item.name, res_item.id, res_item.filemode) == (
        one_file.name,
        one_file.id,
        one_file.filemode,
    )


def test_no_original_different_commit_and_rebased(tmp_path):
    repo = create_repository(tmp_path)

    hello_id = repo.create_blob("hello world")
    buh_bye_id = repo.create_blob("buh bye")

    tree_builder = repo.TreeBuilder()
    tree_builder.insert("hello", hello_id, FileMode.BLOB)
    tree_builder.insert("bye", buh_bye_id, FileMode.BLOB)
    tree = repo.get(tree_builder.write())

    hello = tree["hello"]
    bye = tree["bye"]

    assert easy_merge(hello, None, bye) == (False, None)


def test_differing_commit_and_original_empty_rebased(tmp_path):
    repo = create_repository(tmp_path)

    hello_id = repo.create_blob("hello world")
    buh_bye_id = repo.create_blob("buh bye")

    tree_builder = repo.TreeBuilder()
    tree_builder.insert("hello", hello_id, FileMode.BLOB)
    tree_builder.insert("bye", buh_bye_id, FileMode.BLOB)
    tree = repo.get(tree_builder.write())

    hello = tree["hello"]
    bye = tree["bye"]

    assert easy_merge(hello, bye, None) == (False, None)
