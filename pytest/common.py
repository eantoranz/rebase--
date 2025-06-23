# copyright (c) 2025 Edmundo Carmona Antoranz
# Released under the terms of GPLv2.0

import pygit2


USER_NAME = "Fulanito D'Tal"
USER_EMAIL = "fulanito@foo.bar"

def create_repository(path):
    repo = pygit2.init_repository(path, bare=True)
    repo.config["user.name"] = USER_NAME
    repo.config["user.email"] = USER_EMAIL
    return repo


def create_test_tree():
    # - If adding a blob, the item will be added into the tree like this:
    # parent_tree[path] = (FileMode, content)
    # - If adding a (child) tree, the item will be saved like this:
    # parent_tree[path] = child_tree
    return {}


def add_test_blob(tree, path: str, mode: pygit2.enums.FileMode, content):
    assert path.find("/") == -1
    assert mode in (pygit2.enums.FileMode.BLOB, pygit2.enums.FileMode.BLOB_EXECUTABLE)
    tree[path] = (mode, content)


def add_test_tree(parent_tree, path):
    assert path.find("/") == -1
    child_tree = {}
    parent_tree[path] = child_tree
    return child_tree


def write_test_tree(repo, tree, root_tree=True):
    tree_builder = repo.TreeBuilder()
    for path, tree_item in tree.items():
        if isinstance(tree_item, tuple):
            mode, content = tree_item
            blob_id = repo.create_blob(content)
            tree_builder.insert(path, blob_id, mode)
        else:
            # it is a tree
            child_tree_id = write_test_tree(repo, tree_item, False)
            if child_tree_id is None:
                continue  # tree was empty
            tree_builder.insert(path, child_tree_id, pygit2.enums.FileMode.TREE)
    if not root_tree and len(tree_builder) == 0:
        return (
            None  # avoid writing this tree as it is empty and it's _not_ the root tree
        )
    tree_id = tree_builder.write()
    return tree_id


def create_commit(repo, root_tree, message, parents=[]):
    if isinstance(root_tree, pygit2.Tree):
        root_tree_id = root_tree.id
    elif isinstance(root_tree, pygit2.Oid):
        root_tree_id = root_tree
    else:
        root_tree_id = write_test_tree(repo, root_tree)
    # now we create the commit
    signature = pygit2.Signature(USER_NAME, USER_EMAIL)
    commit_id = repo.create_commit(
        None, signature, signature, message, root_tree_id, parents
    )
    return commit_id


def remove_tree_item(tree, path):
    assert path.find("/") == -1
    if path in tree:
        del tree[path]


def get_tree_item(tree, path):
    assert path.find("/") == -1
    return tree.get(path, None)
