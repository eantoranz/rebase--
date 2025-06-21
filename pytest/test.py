# Copyright (c) 2025 Edmundo Carmona Antoranz
# Released under the terms of GPLv2

import pygit2

from rebasedashdash import rebase


def test_simple_rebase():
    repo = pygit2.Repository("pytest/repos/test_simple_rebase")
    assert repo is not None

    # let's run a rebase
    main = repo.revparse_single("main")
    test = repo.revparse_single("test")
    assert all(
        item is not None and isinstance(item, pygit2.Commit) for item in [main, test]
    )

    conflicts = []
    result = rebase(repo, main, test, main, conflicts)
    assert isinstance(result, pygit2.Commit)
    assert main.id != result.id
    assert test.id != result.id
    assert len(conflicts) == 0

    hello_world = (
        "Hello world\n"
        "\n"
        "We are modifying the middle of the file\n"
        "\n"
        "We are modifying the end of the file\n"
    )

    assert hello_world == result.tree["hello_world.txt"].data.decode()


def test_simple_merge_commit():
    repo = pygit2.Repository("pytest/repos/test_simple_merge_commit")
    assert repo is not None

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

    assert result.tree["non-executable"].filemode == pygit2.enums.FileMode.BLOB_EXECUTABLE
    assert result.tree["final-executable-from-main"].filemode == pygit2.enums.FileMode.BLOB_EXECUTABLE
    assert result.tree["final-executable-from-A"].filemode == pygit2.enums.FileMode.BLOB_EXECUTABLE

    assert result.tree["separate-file.txt"] is not None

    executable = (
        "This is an executable file\n"
        "\n"
        "Modifying the middle of the file in main... we will make it non-executable\n"
        "\n"
        "Modifying the end of the file in A\n"
    )
    assert result.tree["executable"].filemode == pygit2.enums.FileMode.BLOB
    assert result.tree["executable"].data.decode() == executable

    non_executable = (
        "This is a non-executable file\n"
        "\n"
        "Modifying the middle of the file in A... we will make it executable\n"
        "\n"
        "Modifying the end of the file in main\n"
    )
    assert result.tree["non-executable"].filemode == pygit2.enums.FileMode.BLOB_EXECUTABLE
    assert result.tree["non-executable"].data.decode() == non_executable


def test_conflicting_blob_merge_commit():
    repo = pygit2.Repository("pytest/repos/test_conflicting_blob_merge_commit")
    assert repo is not None

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

    separate_file = "This is a separate file\n"
    hello_world = (
        "Hello world\n"
        "\n"
        "This is how we solved the conflict\n"
        "\n"
        "Wrapping up the file\n"
    )

    assert separate_file == result.tree["separate-file.txt"].data.decode()
    assert hello_world == result.tree["hello_world.txt"].data.decode()


def test_conflicting_blob_merge_commit_change_upstream():
    repo = pygit2.Repository(
        "pytest/repos/test_conflicting_blob_merge_commit_change_upstream"
    )
    assert repo is not None

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


def test_deleted_blob():
    repo = pygit2.Repository("pytest/repos/test_deleted_blob")
    assert repo is not None

    main = repo.revparse_single("main")
    other = repo.revparse_single("other")
    assert all(
        item is not None and isinstance(item, pygit2.Commit) for item in [main, other]
    )

    conflicts = []
    result = rebase(repo, main, other, main.parents[0], conflicts)
    assert isinstance(result, pygit2.Commit)
    assert main.id != result.id
    assert other.id != result.id
    assert len(conflicts) == 0
    assert len(result.tree) == 1

    another = "Ok, Ok... so I did modify it. Sue me!\n"
    assert another == result.tree["another.txt"].data.decode()

    result2 = rebase(repo, main, result, main, conflicts)
    assert isinstance(result2, tuple)
    assert len(conflicts) == 1


def test_empty_root_dir():
    repo = pygit2.Repository("pytest/repos/test_empty_root_dir")
    assert repo is not None

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


def test_reuse_commits():
    repo = pygit2.Repository("pytest/repos/test_reuse_commits")
    assert repo is not None

    main = repo.revparse_single("main")
    base = repo.revparse_single("main~2")
    assert all(
        item is not None and isinstance(item, pygit2.Commit) for item in [main, base]
    )

    conflicts = []
    result = rebase(repo, base, main, base, conflicts)
    assert isinstance(result, pygit2.Commit)
    assert main.id == result.id