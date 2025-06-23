# Copyright (c) 2025 Edmundo Carmona Antoranz
# Released under the terms of GPLv2.0

import copy
import pygit2

from rebasedashdash import rebase

from common import add_test_blob
from common import create_commit
from common import create_repository
from common import create_test_tree


def test_simple_merge_commit(tmp_path):
    # * EEEE (B) Adding a separate file
    # | *   DDDD (main) merging branch A
    # | | \
    # | | * CCCC (A) non-executable content is modified and changed to executable, executable is only modified in content, also executable-from-A is made into executable
    # | |/
    # |/|
    # | * BBBB executable content is modified and changed to non-executable, non-executable is only modified in content, executable-from-main is turned into executable
    # |/
    # * AAA Adding an executable and a non-executable file, also two files that will will only change their executable flags (one from each branch)
    repo = create_repository(tmp_path)

    root_tree_main = create_test_tree()
    executable = (
        "This is an executable file\n"
        "\n"
        "This is the initial commit of the file\n"
        "\n"
        "Wrapping up the file\n"
    )
    add_test_blob(
        root_tree_main, "executable", pygit2.enums.FileMode.BLOB_EXECUTABLE, executable
    )
    non_executable = (
        "This is a non-executable file\n"
        "\n"
        "This is the initial commit of the file\n"
        "\n"
        "Wrapping up the file\n"
    )
    add_test_blob(
        root_tree_main, "non-executable", pygit2.enums.FileMode.BLOB, non_executable
    )
    final_executable_from_main = (
        "This file will be turned into executable from main branch\n"
    )
    add_test_blob(
        root_tree_main,
        "final-executable-from-main",
        pygit2.enums.FileMode.BLOB,
        final_executable_from_main,
    )
    final_executable_from_A = "This file will be turned into executable from branch A\n"
    add_test_blob(
        root_tree_main,
        "final-executable-from-A",
        pygit2.enums.FileMode.BLOB,
        final_executable_from_A,
    )

    main_commits = [
        create_commit(
            repo,
            root_tree_main,
            "Adding an executable and a non-executable file, also two files that will will only change their executable flags (one from each branch)",
        )
    ]

    root_tree_A = copy.deepcopy(root_tree_main)
    A_commits = copy.copy(main_commits)

    root_tree_B = copy.deepcopy(root_tree_main)
    B_commits = copy.copy(main_commits)

    executable = (
        "This is an executable file\n"
        "\n"
        "Modifying the middle of the file in main... we will make it non-executable\n"
        "\n"
        "Wrapping up the file\n"
    )
    add_test_blob(root_tree_main, "executable", pygit2.enums.FileMode.BLOB, executable)
    non_executable = (
        "This is a non-executable file\n"
        "\n"
        "This is the initial commit of the file\n"
        "\n"
        "Modifying the end of the file in main\n"
    )
    add_test_blob(
        root_tree_main, "non-executable", pygit2.enums.FileMode.BLOB, non_executable
    )  # it is still non-executable
    add_test_blob(
        root_tree_main,
        "final-executable-from-main",
        pygit2.enums.FileMode.BLOB_EXECUTABLE,
        final_executable_from_main,
    )  # no change in content, just the filemode

    main_commits.append(
        create_commit(
            repo,
            root_tree_main,
            "executable content is modified and changed to non-executable, non-executable is only modified in content, executable-from-main is turned into executable",
            main_commits,
        )
    )

    # switching to A
    executable = (
        "This is an executable file\n"
        "\n"
        "This is the initial commit of the file\n"
        "\n"
        "Modifying the end of the file in A\n"
    )
    add_test_blob(
        root_tree_A, "executable", pygit2.enums.FileMode.BLOB_EXECUTABLE, executable
    )
    non_executable = (
        "This is a non-executable file\n"
        "\n"
        "Modifying the middle of the file in A... we will make it executable\n"
        "\n"
        "Wrapping up the file\n"
    )
    add_test_blob(
        root_tree_A,
        "non-executable",
        pygit2.enums.FileMode.BLOB_EXECUTABLE,
        non_executable,
    )  # we make it executable
    add_test_blob(
        root_tree_A,
        "final-executable-from-A",
        pygit2.enums.FileMode.BLOB_EXECUTABLE,
        final_executable_from_A,
    )  # no change in content, just the filemode

    A_commits.append(
        create_commit(
            repo,
            root_tree_A,
            "non-executable content is modified and changed to executable, executable is only modified in content, also executable-from-A is made into executable",
            A_commits,
        )
    )

    # we merge A into main
    merge_result = repo.merge_commits(main_commits[-1], A_commits[-1])
    assert merge_result.conflicts is None
    main_commits.append(
        create_commit(
            repo, merge_result.write_tree(), "", [main_commits[-1], A_commits[-1]]
        )
    )

    # verify result of merge
    main_tree = repo.get(main_commits[-1]).tree
    executable = (
        "This is an executable file\n"
        "\n"
        "Modifying the middle of the file in main... we will make it non-executable\n"
        "\n"
        "Modifying the end of the file in A\n"
    )
    assert main_tree["executable"].data.decode() == executable
    non_executable = (
        "This is a non-executable file\n"
        "\n"
        "Modifying the middle of the file in A... we will make it executable\n"
        "\n"
        "Modifying the end of the file in main\n"
    )

    assert main_tree["executable"].data.decode() == executable
    assert main_tree["non-executable"].data.decode() == non_executable

    assert main_tree["executable"].filemode == pygit2.enums.FileMode.BLOB
    assert main_tree["non-executable"].filemode == pygit2.enums.FileMode.BLOB_EXECUTABLE
    assert (
        main_tree["final-executable-from-main"].filemode
        == pygit2.enums.FileMode.BLOB_EXECUTABLE
    )
    assert (
        main_tree["final-executable-from-A"].filemode
        == pygit2.enums.FileMode.BLOB_EXECUTABLE
    )

    repo.references.create("refs/heads/main", main_commits[-1])
    repo.references.create("refs/heads/A", A_commits[-1])

    # switch into B and add a separate file that does not mess with the merge
    separate_file = "This is a separate file"
    add_test_blob(
        root_tree_B, "separate-file.txt", pygit2.enums.FileMode.BLOB, separate_file
    )

    B_commits.append(
        create_commit(repo, root_tree_B, "Adding a separate file", [B_commits[-1]])
    )

    repo.references.create("refs/heads/B", B_commits[-1])

    B = repo.revparse_single("B")
    main = repo.revparse_single("main")
    A = repo.revparse_single("A")
    assert all(
        item is not None and isinstance(item, pygit2.Commit) for item in [main, B]
    )

    conflicts = []
    result = rebase(repo, B, main, B, conflicts)
    assert isinstance(result, pygit2.Commit)
    assert B.id != result.id
    assert main.id != result.id
    assert len(result.parents) == 2
    assert result.parents[0] not in main.parents
    assert result.parents[0] != A.id
    assert result.parents[1] not in main.parents
    assert result.parents[1] != A.id
    assert len(conflicts) == 0

    assert (
        result.tree["non-executable"].filemode == pygit2.enums.FileMode.BLOB_EXECUTABLE
    )
    assert (
        result.tree["final-executable-from-main"].filemode
        == pygit2.enums.FileMode.BLOB_EXECUTABLE
    )
    assert (
        result.tree["final-executable-from-A"].filemode
        == pygit2.enums.FileMode.BLOB_EXECUTABLE
    )

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
    assert (
        result.tree["non-executable"].filemode == pygit2.enums.FileMode.BLOB_EXECUTABLE
    )
    assert result.tree["non-executable"].data.decode() == non_executable
