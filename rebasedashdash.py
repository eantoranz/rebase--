# Copyright (c) 2025 Edmundo Carmona Antoranz
# Released under the terms of GPLv2

# part of rebase--
# https://github.com/eantoranz/rebase--

import pygit2
import sys
import typing
from collections.abc import Callable
from enum import Enum


if not hasattr(pygit2, "enums"):
    sys.stderr.write(
        f"You are using a version of pygit2 that is too old.\n"
        f"pygit2 version: {pygit2.__version__}\n"
        "Try switching to a newer version of it.\n"
    )
    sys.stderr.flush()
    sys.exit(1)


class RebaseAction(Enum):
    REBASED = 1  # the commit was rebased
    REUSED = 2  # the commit was skipped
    CONFLICTS = 3  # There were conflicts dealing with this commit


class TreesIterator:

    def next_tree_item(self, tree_iterator):  # TODO what is the type of an interator?
        if tree_iterator is None:
            return None
        try:
            return tree_iterator.__next__()
        except StopIteration:
            return None

    def __init__(
        self,
        original_tree: pygit2.Tree,
        original_parent_trees: list[pygit2.Tree],
        rebased_parent_trees: list[pygit2.Tree],
    ):
        self.original_tree = original_tree
        self.original_parent_trees = original_parent_trees
        self.rebased_parent_trees = rebased_parent_trees

        self.original_tree_iterator = (
            original_tree.__iter__() if original_tree else None
        )
        self.original_parent_iterators = list(
            (parent.__iter__() if parent else None) for parent in original_parent_trees
        )
        self.rebased_parent_iterators = list(
            (parent.__iter__() if parent else None) for parent in rebased_parent_trees
        )

        self.original_tree_item = self.next_tree_item(self.original_tree_iterator)
        self.original_parent_tree_items = list(
            self.next_tree_item(parent_tree_iterator)
            for parent_tree_iterator in self.original_parent_iterators
        )
        self.rebased_parent_tree_items = list(
            self.next_tree_item(parent_tree_iterator)
            for parent_tree_iterator in self.rebased_parent_iterators
        )

    def _get_next_path(self) -> typing.Union[str, None]:
        # Will return None if there are no more paths
        next_path = None
        items = list()
        if self.original_tree_item:
            items.append(self.original_tree_item)
        items.extend(item for item in self.original_parent_tree_items if item)
        items.extend(item for item in self.rebased_parent_tree_items if item)
        for item in items:
            if next_path is None:
                next_path = item.name
            else:
                if item.name < next_path:
                    next_path = item.name
        return next_path

    def _move_items_forward(self, path: str):
        if self.original_tree_item and self.original_tree_item.name == path:
            self.original_tree_item = self.next_tree_item(self.original_tree_iterator)
        for i in range(len(self.original_parent_tree_items)):
            item = self.original_parent_tree_items[i]
            if item and item.name == path:
                self.original_parent_tree_items[i] = self.next_tree_item(
                    self.original_parent_iterators[i]
                )
            item = self.rebased_parent_tree_items[i]
            if item and item.name == path:
                self.rebased_parent_tree_items[i] = self.next_tree_item(
                    self.rebased_parent_iterators[i]
                )

    def next_tree_items(
        self,
    ) -> typing.Union[
        tuple[
            str,
            typing.Union[pygit2.Object, None],
            list[typing.Union[pygit2.Object, None]],
            list[typing.Union[pygit2.Object, None]],
        ],
        None,
    ]:
        next_path = self._get_next_path()
        if next_path is None:
            # we are finished
            return None
        original_tree_item = (
            self.original_tree_item
            if self.original_tree_item and self.original_tree_item.name == next_path
            else None
        )
        original_parent_tree_items = list(
            (parent_item if parent_item and parent_item.name == next_path else None)
            for parent_item in self.original_parent_tree_items
        )
        rebased_parent_tree_items = list(
            (parent_item if parent_item and parent_item.name == next_path else None)
            for parent_item in self.rebased_parent_tree_items
        )

        # get next item for the trees that matched the path
        self._move_items_forward(next_path)
        return (
            next_path,
            original_tree_item,
            original_parent_tree_items,
            rebased_parent_tree_items,
        )


def objects_match(object1: pygit2.Object, object2: pygit2.Object) -> bool:
    if object1 is None and object2 is None:
        return True
    if object1 is None or object2 is None:
        return False
    return (object1.id, object1.name, object1.type) == (
        object2.id,
        object2.name,
        object2.type,
    ) and (
        object1.type != pygit2.enums.ObjectType.BLOB
        # if they are blobs, the filemode has to match too
        or object1.filemode == object2.filemode
    )


def easy_merge(
    commit_item: typing.Union[pygit2.Object, None],
    original_item: typing.Union[pygit2.Object, None],
    rebased_item: typing.Union[pygit2.Object, None],
) -> tuple[bool, typing.Union[pygit2.Object, None]]:

    if objects_match(original_item, rebased_item):
        # straight one
        return True, commit_item

    item_to_commit = None
    solved = False
    if commit_item is None:
        # parents are different cause we would not be here otherwise
        if original_item is None:
            # we can use the rebased parent item
            return True, rebased_item
        if rebased_item is None:
            # it is already deleted in the rebased tree.. so change is already applied, right?
            return True, None
        # If we are here, this is a tree conflict (deleted by them)
    else:
        # commit tree is set
        # we know that original/rebased parents are not the same
        if original_item is None:
            # rebased parent must set
            if objects_match(rebased_item, commit_item):
                solved, item_to_commit = True, commit_item
            else:
                # no easy resolution
                pass
        else:
            # original parent is set
            if objects_match(commit_item, original_item):
                # we can use the rebased parent item
                solved, item_to_commit = True, rebased_item
            else:
                if rebased_item is None:
                    # no easy fix
                    pass
                else:
                    # rebased parent item is set
                    if objects_match(rebased_item, commit_item):
                        # the change has already been applied on rebased_parent_item
                        solved, item_to_commit = True, rebased_item
                    else:
                        # no easy fix
                        pass

    return solved, item_to_commit


def merge_blobs_3way(
    repo: pygit2.Repository,
    ancestor: typing.Union[tuple[pygit2.Oid, pygit2.enums.FileMode], None],
    ours: typing.Union[tuple[pygit2.Oid, pygit2.enums.FileMode], None],
    theirs: typing.Union[tuple[pygit2.Oid, pygit2.enums.FileMode], None],
) -> typing.Union[
    tuple[pygit2.Oid, pygit2.enums.FileMode], pygit2.Index
]:  # returning the index means there was a conflict, tuple[Blob, filemode]
    # deal with the easy ones first
    if ours == theirs or theirs == ancestor:
        return ours
    if ours == ancestor:
        return theirs

    # FIXME Ugh... I hate creating trees just for this but I see no support for 3-way merges of blobs in pygit2 so....
    tree_builder_p1 = repo.TreeBuilder()
    if ours:
        tree_builder_p1.insert("a", ours[0], ours[1])

    tree_builder_p2 = repo.TreeBuilder()
    if theirs:
        tree_builder_p2.insert("a", theirs[0], theirs[1])

    tree_builder_a = repo.TreeBuilder()
    if ancestor:
        tree_builder_a.insert("a", ancestor[0], ancestor[1])

    merge_result = repo.merge_trees(
        tree_builder_a.write(), tree_builder_p1.write(), tree_builder_p2.write()
    )

    if merge_result.conflicts:
        return merge_result

    result_index_item = merge_result["a"]
    if result_index_item is None:
        return None

    # TODO Try to get the value of the mode in the resulting blob so that we do not have to deal with it separately
    return result_index_item.id, result_index_item.mode


class CommitMetadata:
    repo: pygit2.Repository
    commit: pygit2.Commit
    _merge_base: typing.Union[
        pygit2.Commit, None, bool
    ]  # False if it hasn't been set yet, None if there is no merge base
    rebased_parents: list[pygit2.Commit]
    _rebased_merge_base: typing.Union[
        pygit2.Commit, None, bool
    ]  # False if it hasn't been set yet, None if there is no merge base

    def __init__(
        self,
        repo: pygit2.Repository,
        commit: pygit2.Commit,
        rebased_parents: list[pygit2.Commit],
    ):
        self.repo = repo
        self.commit = commit
        self.rebased_parents = rebased_parents
        self._rebased_merge_base = False
        self._merge_base = False
        assert len(self.commit.parents) == len(rebased_parents)

    def _get_merge_bases(self):
        if self._merge_base == False:
            if len(self.rebased_parents) == 0:
                self._merge_base = None
                self._rebased_merge_base = None
            elif len(self.rebased_parents) == 1:
                self._merge_base = self.commit.parents[0]
                self._rebased_merge_base = self.rebased_parents[0]
            else:
                self._merge_base = self.repo.merge_base_many(
                    [parent.id for parent in self.commit.parents]
                )
                if self._merge_base is not None:
                    self._merge_base = self.repo.get(self._merge_base)
                self._rebased_merge_base = self.repo.merge_base_many(
                    [parent.id for parent in self.rebased_parents]
                )
                if self._rebased_merge_base is not None:
                    self._rebased_merge_base = self.repo.get(self._rebased_merge_base)

    @property
    def merge_base(self) -> typing.Union[pygit2.Commit, None]:
        self._get_merge_bases()
        return self._merge_base

    @property
    def rebased_merge_base(self) -> typing.Union[pygit2.Commit, None]:
        self._get_merge_bases()
        return self._rebased_merge_base


def merge_blobs(
    commit_metadata: CommitMetadata,
    path: str,
    commit_blob: typing.Union[pygit2.Blob, None],
    original_parent_blobs: list[typing.Union[pygit2.Blob, None]],
    rebased_parent_blobs: list[typing.Union[pygit2.Blob, None]],
) -> typing.Union[
    tuple[pygit2.Oid, int], None, bool
]:  # None means a deleted Blob, False means there was a conflict, tuple[Blob, filemode]
    assert commit_blob is None or isinstance(commit_blob, pygit2.Blob)
    assert len(original_parent_blobs) == len(rebased_parent_blobs)
    assert all(
        (parent is None or isinstance(parent, pygit2.Blob))
        for parent in original_parent_blobs
    )
    assert all(
        (parent is None or isinstance(parent, pygit2.Blob))
        for parent in rebased_parent_blobs
    )

    # we assume that if we are here, all the pairs of original_parent_blob/rebased_parent_blob are differing.
    # Also, the easy single-parent cases where we can easily find a resulting object have already
    # been taken care of. Here we are dealing with the _hard_ merges only.

    if len(original_parent_blobs) == 1:
        result = merge_blobs_3way(
            commit_metadata.repo,
            (
                (original_parent_blobs[0].id, original_parent_blobs[0].filemode)
                if original_parent_blobs[0]
                else None
            ),
            (commit_blob.id, commit_blob.filemode) if commit_blob else None,
            (
                (rebased_parent_blobs[0].id, rebased_parent_blobs[0].filemode)
                if rebased_parent_blobs[0]
                else None
            ),
        )
        if result is None or isinstance(result, tuple):
            return result

        # last resort: checking against the common ancestor of the parent commits
        if len(commit_metadata.commit.parents) > 1:
            # the other parents are the same between original and rebased parents
            # if the original_parent_blob is the same as in the merge_base of the parents of the original commit
            # we can take the original commit object
            merge_base = commit_metadata.merge_base
            if merge_base is not None:
                if path in merge_base.tree:
                    ancestor_object = merge_base.tree[path]
                else:
                    ancestor_object = None
                if objects_match(ancestor_object, original_parent_blobs[0]):
                    # let's make sure that it did not change on the other side
                    rebased_merge_base = commit_metadata.rebased_merge_base
                    if rebased_merge_base is not None:
                        if path in rebased_merge_base.tree:
                            rebased_ancestor_object = rebased_merge_base.tree[path]
                        else:
                            rebased_ancestor_object = None
                        if objects_match(
                            rebased_ancestor_object, rebased_parent_blobs[0]
                        ):
                            return commit_blob.id, commit_blob.filemode

        # if there is a conflict this way, it is not possible to solve it differently
        return False

    if (
        commit_blob is not None
        and all(parent is not None for parent in original_parent_blobs)
        and all(parent is not None for parent in rebased_parent_blobs)
    ):
        # dealing with a multi-parent conflict
        result_blob = (commit_blob.id, commit_blob.filemode)
        for original_parent_blob, rebased_parent_blob in zip(
            original_parent_blobs, rebased_parent_blobs
        ):
            # we do not want to have to deal with filemode changes at the moment
            if (
                original_parent_blob.filemode != commit_blob.filemode
                or rebased_parent_blob.filemode != commit_blob.filemode
            ):
                result_blob = None
                break
            merge_result = merge_blobs_3way(
                commit_metadata.repo,
                (original_parent_blob.id, original_parent_blob.filemode),
                result_blob,
                (rebased_parent_blob.id, rebased_parent_blob.filemode),
            )
            if isinstance(merge_result, pygit2.Index):
                # there was a conflict, sorry but we can't continue
                # and we do not have a resolution yet
                result_blob = None
                break
            result_blob = merge_result  # take the blob as it is right now
        if result_blob:
            # we have a successful merge
            return result_blob

    # for the time being, we will just say there was a conflict
    return False


# TODO is it ok to only consider _differing_ parents? (trees, blobs)
# I have a hunch this is way too optimistic.
def merge_trees(
    commit_metadata: CommitMetadata,
    commit_tree: typing.Union[
        pygit2.Tree, None
    ],  # TODO not necessarily a root tree so maybe a better name would clear it up
    orig_parent_trees: list[typing.Union[pygit2.Tree, None]],
    rebased_parent_trees: list[typing.Union[pygit2.Tree, None]],
    conflicts: list[
        tuple[
            str,
            typing.Union[pygit2.Object, None],
            list[typing.Union[pygit2.Object, None]],
            list[typing.Union[pygit2.Object, None]],
        ]
    ],
    paths: list[str] = [],
) -> typing.Union[
    pygit2.Oid, None, bool
]:  # None if the result is an empty/deleted tree, False if we have a tree conflict
    assert commit_tree is None or isinstance(commit_tree, pygit2.Tree)
    assert len(orig_parent_trees) == len(rebased_parent_trees)
    assert all(
        (parent is None or isinstance(parent, pygit2.Tree))
        for parent in orig_parent_trees
    )
    assert all(
        (parent is None or isinstance(parent, pygit2.Tree))
        for parent in rebased_parent_trees
    )

    # the following sanity check has to be carried out on a root tree
    # if we are working on a recursive call, this check has already been carried out
    if not paths:
        differing_parents = set()  # each item is a tuple (original tree, rebased tree)
        for orig_parent_tree, rebased_parent_tree in zip(
            orig_parent_trees, rebased_parent_trees
        ):
            if orig_parent_tree == rebased_parent_tree:
                # also works for None
                continue
            if (
                orig_parent_tree is None
                or rebased_parent_tree is None
                or orig_parent_tree.id != rebased_parent_tree.id
            ):
                differing_parents.add((orig_parent_tree, rebased_parent_tree))
        if not differing_parents:
            # we can take the original tree as a whole
            return commit_tree.id

        # if dealing with single "differing" parent commits, there are a few other possibilities using the rebased parent tree
        if len(differing_parents) == 1:
            orig_parent_tree, rebased_parent_tree = list(differing_parents)[0]
            easy_solution = easy_merge(
                commit_tree, orig_parent_tree, rebased_parent_tree
            )
            if easy_solution[0]:
                # it was solved
                return easy_solution[1].id

    # not everything in the trees matches.... can we solve this puzzle?
    # We need to walk over the items in the trees, both sets of parents and commit_tree.
    # If we are lucky, we will be able to find correct resolutions for all the
    # separate items in the trees.
    trees_iterator = TreesIterator(commit_tree, orig_parent_trees, rebased_parent_trees)
    tree_builder = commit_metadata.repo.TreeBuilder()
    while tree_items := trees_iterator.next_tree_items():
        path, commit_tree_item, original_parent_items, rebased_parent_items = tree_items
        differing_parents = set()  # each item is a tuple (original item, rebased item)
        for original_parent_item, rebased_parent_item in zip(
            original_parent_items, rebased_parent_items
        ):
            if original_parent_item == rebased_parent_item:
                continue
            if (
                original_parent_item is None
                or rebased_parent_item is None
                or (original_parent_item.id != rebased_parent_item.id)
            ):
                differing_parents.add((original_parent_item, rebased_parent_item))

        if not differing_parents:
            if commit_tree_item:
                tree_builder.insert(
                    path, commit_tree_item.id, commit_tree_item.filemode
                )
            continue

        # not everything matches

        if len(differing_parents) == 1:
            differing_parents = list(differing_parents)
            # Is it still possible to use an easy conflict resolution?
            original_parent_item, rebased_parent_item = list(differing_parents)[0]
            solved, item_to_commit = easy_merge(
                commit_tree_item, original_parent_item, rebased_parent_item
            )

            if solved:
                if item_to_commit is not None:
                    tree_builder.insert(
                        path,
                        item_to_commit.id,
                        item_to_commit.filemode,
                    )
                continue

        # if we are wondering around here we have like a _real_ conflict of some kind

        if (
            commit_tree_item is None or isinstance(commit_tree_item, pygit2.Tree)
        ) and all(
            (orig_parent is None or isinstance(orig_parent, pygit2.Tree))
            and (rebased_parent is None or isinstance(rebased_parent, pygit2.Tree))
            for orig_parent, rebased_parent in differing_parents
        ):
            # we we are dealing with trees, we can recurse into them
            original_differing_parent_items, rebased_differing_parent_items = zip(
                *differing_parents
            )
            paths.append(path)
            recursive_result = merge_trees(
                commit_metadata,
                commit_tree_item,
                original_differing_parent_items,
                rebased_differing_parent_items,
                conflicts,
                paths,
            )
            del paths[-1]
            if (
                recursive_result is None
                or isinstance(recursive_result, pygit2.Tree)
                and len(recursive_result) == 0
            ):
                # tree was deleted
                continue
            # a non-empty real tree or a conflict
            # if there is a conflict, it has been taken care of at the "leaves" (blobs) level
            if recursive_result:
                # a non-empty tree
                tree_builder.insert(path, recursive_result, pygit2.enums.FileMode.TREE)
            continue  # go to the next tree item

        if (
            commit_tree_item is None or isinstance(commit_tree_item, pygit2.Blob)
        ) and all(
            (orig_parent is None or isinstance(orig_parent, pygit2.Blob))
            and (rebased_parent is None or isinstance(rebased_parent, pygit2.Blob))
            for orig_parent, rebased_parent in differing_parents
        ):
            # we are dealing with blobs, we can try to find a way to merge them
            original_differing_parent_items, rebased_differing_parent_items = zip(
                *differing_parents
            )
            paths.append(path)
            fullpath = "/".join(paths)
            blob_result = merge_blobs(
                commit_metadata,
                fullpath,
                commit_tree_item,
                original_differing_parent_items,
                rebased_differing_parent_items,
            )
            del paths[-1]
            if blob_result is None or isinstance(blob_result, tuple):
                # we were able to solve it
                if blob_result is not None:
                    tree_builder.insert(
                        path,
                        blob_result[0],
                        blob_result[1],
                    )
            else:
                conflicts.append(
                    (
                        fullpath,
                        commit_tree_item,
                        original_parent_items,
                        rebased_parent_items,
                    )
                )
            continue

        # if we are wondering around here we have like a _real_ conflict that we could not solve
        paths.append(path)
        fullpath = "/".join(paths)
        del paths[-1]
        conflicts.append(
            (fullpath, commit_tree_item, original_parent_items, rebased_parent_items)
        )
        continue

    if len(tree_builder):
        return tree_builder.write()
    return None


class RebaseOptions:
    upstream: pygit2.Commit = None
    source: pygit2.Commit
    onto: typing.Union[pygit2.Commit, None]
    progress_hook: Callable = (
        None  # hook that will be called when we have figured out what happened with a commit
    )
    force_rebase: bool = False

    def __init__(
        self,
        upstream: pygit2.Commit,
        source: pygit2.Commit,
        onto: typing.Union[pygit2.Commit, None] = None,
    ):
        self.upstream = upstream
        self.source = source
        self.onto = onto


def rebase(
    repo: pygit2.Repository,
    rebase_options: RebaseOptions,
    conflicts: list[
        tuple[
            str,
            typing.Union[pygit2.Object, None],
            list[typing.Union[pygit2.Object, None]],
            list[typing.Union[pygit2.Object, None]],
        ]
    ],
) -> typing.Union[
    pygit2.Commit, tuple[str, pygit2.Commit, dict[pygit2.Oid, pygit2.Commit]]
]:  # tuple if there is a problem, indicate the reason, the commit, and the current mapping of commits

    assert rebase_options.upstream is not None
    assert rebase_options.source is not None

    upstream = rebase_options.upstream
    source = rebase_options.source
    onto = rebase_options.onto

    if onto is None:
        onto = upstream

    # lookfor commits to rebase
    signature = pygit2.Signature(
        repo.config.__getitem__("user.name"),
        repo.config.__getitem__("user.email"),
    )

    merge_base_id = repo.merge_base(source.id, upstream.id)
    if merge_base_id is None:
        return "No merge base between the upstream and the source", None, None

    rebase_walker = repo.walk(
        source.id, pygit2.enums.SortMode.TOPOLOGICAL | pygit2.enums.SortMode.REVERSE
    )
    rebase_walker.hide(merge_base_id)

    commits_to_rebase = list(rebase_walker)

    # mappings between original commits and their resulting equivalents
    commits_map = {merge_base_id: onto}
    counter = 0
    commits_count = len(commits_to_rebase)
    # the items in the conflicts tuple: path, rebased object, original parents, rebased parents

    for rebased_commit in commits_to_rebase:
        counter += 1

        orig_parents = rebased_commit.parents
        orig_parent_trees = [parent.tree for parent in orig_parents]
        rebased_parents = [
            commits_map.get(orig_parent.id, orig_parent) for orig_parent in orig_parents
        ]
        rebased_parent_trees = [parent.tree for parent in rebased_parents]

        if not rebase_options.force_rebase and all(
            commits_map.get(parent.id, parent) == parent
            for parent in rebased_commit.parents
        ):
            # this commit can be reused as all parents are exactly the same between old and rebased commit
            if rebase_options.progress_hook is not None:
                rebase_options.progress_hook(
                    RebaseAction.REUSED, counter, commits_count
                )
            commits_map[rebased_commit.id] = rebased_commit
            continue

        commit_metadata = CommitMetadata(repo, rebased_commit, rebased_parents)

        result_tree = merge_trees(
            commit_metadata,
            rebased_commit.tree,
            orig_parent_trees,
            rebased_parent_trees,
            conflicts,
        )
        if conflicts:
            # There were conflicts
            if rebase_options.progress_hook is not None:
                rebase_options.progress_hook(
                    RebaseAction.CONFLICTS, counter, commits_count
                )
            return f"There were conflicts", rebased_commit, commits_map

        if result_tree is None:
            # is there a constant for an empty tree?
            result_tree = repo.TreeBuilder().write()

        rebased_parent_ids = [parent.id for parent in rebased_parents]
        new_commit = repo.create_commit(
            None,
            rebased_commit.author,
            signature,
            rebased_commit.message,
            result_tree,
            rebased_parent_ids,
        )

        new_commit = repo.get(new_commit)
        commits_map[rebased_commit.id] = new_commit
        if rebase_options.progress_hook is not None:
            rebase_options.progress_hook(RebaseAction.REBASED, counter, commits_count)

    return commits_map[commits_to_rebase[-1].id]
