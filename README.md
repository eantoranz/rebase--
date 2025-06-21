# rebase--

The back-to-basics rebasing tool.


# What is rebase--

`rebase--` tries to be a simple rebase tool that
deals with only the most basic rebasing scenarios
while also trying to overcome the simplest of 
conflicts.

It is not intended to become a full replacement of `git-rebase`. Only
being able to _easily_ deal with the most-basic scenarios and deal with
them _fast_.


# why rebase--?
`git-rebase` is a very powerful tool. It has many very powerful options to carry out many
different tasks for many different purposes and use cases. _Unfortunately_, to be able to
fulfill all of those requirements, it makes it cumbersome to work on a few scenarios.

- `git-rebase` needs to carry out its work moving around the working tree. This means
  that `HEAD` will need to be moved around to all the new commits during the rebase.
- `git-rebase`, **by default**, recreates a linear history of commits from the original
  commits that are being rebased **and**, most notably, it does not carry over merge commits.
  This works fine on scenarios when merges had no conflicts when they were first created **but**
  this becomes a problem when there were changes introduced in the original merge commits that
  are being rebased (normally that would mean there was a conflict but it might also be a change
  introduced on a non-conflict). As the rebase process goes on, those missing changes can start
  to produce conflicts with later commits being rebased that deal with the section
  of code that the skipped merge commits dealt with.
- In cases when you run `git-rebase` using `--rebase-merges`, if there is a conflict when
  merging commits coming out of the rebase, `git-rebase` does **not** consider if the conflicts
  that popped up were already resolved in the original merge commit been rebased. It will stop in
  its tracks and let you figure out how to deal with it to continue with the rebase.

`rebase--` is an attempt at overcoming at least some of those problems:

- It works _in-memory_ (not fully in memory as it writes objects into git's objects database).
  This provides speed and avoids forcefully having to move `HEAD` around...
- .... which implies that it is possible to run a rebase of a _different_ branch from the one you
  are working on and so there is no need to clean your working tree or create a separate working
  tree to be able to run rebases of other branches.
- If a conflict arises when rebasing a merge commit, it will _try_ to use the original
  merge commit to see if the changes applied on it could be cleanly carried over into the
  new merge commit. It is able to cope with changes on a file that do **not** mess with
  sections of code that were changed in the original merge commit.


# features
- rebase history, including merges.
- avoid conflicts **if possible** based on what the commits being rebased did originally.
- work without moving the working tree.
- Allows rebasing (and moving) a local reference without having to move the working tree.
- **Optionally**, move to the final commit of the rebase (with `--for-real/-4r`).
- **Optionally**, move local references without moving the working tree / `HEAD` (with `--for-real/-4r`
  together with `--stay`).
- **Optionally**, can switch to a `detached HEAD` (with `--detach`).


# drawbacks
- no _smart/best-effort_ rename detection.
- no interactive mode.
- no integration/interaction with `git-rebase`.
- it does not allow (currently) to start working on the updated working tree
  in the middle of the rebase if there is a conflict.
- no mechanism to _straighten_ the history being rebased. It's not possible to
  avoid rebasing merge commits.


# standard usage

`rebase--` is used to rebase commits using the same 3 basic parameters of `git-rebase`.

**Important**: Keep in mind that by default, unlike `git-rebase`, it does **not** mess up
with the working tree or the references involved in the rebase. It will only report the final
**commit id** that comes out of the rebase process, if it succeeds. You can use that **commit id**
at will afterwards. If you would like `rebase--` to move your working tree and local reference involved
in the rebase, you need to use the option `--for-real` (or `-4r`, for short).

## rebase onto upstream
```
rebase-- <upstream-branch>
```
`rebase--` will take commits in the range `<upstream-branch>..<current-branch>` and will
apply them on top of `<upstream-branch>`.

## rebase specifying upstream and branch to rebase
```
rebase-- <upstream-branch> <some-branch>
```
`rebase--` will take commits in the range `<upstream-branch>..<some-branch>` and will
apply them on top of `<upstream-branch>`.

## rebase specifying a _different_ point to stack commits onto
```
rebase-- <upstream-branch> <some-branch> --onto <onto-point>
```
`rebase--` will take commits in the range `<upstream-branch>..<some-branch>` and will
apply them on top of `<onto-point>`. This use-case is very useful for moving features around.


# non-standard usage
`rebase--` provides a few options that are not provided by `git-rebase`.

## rebase a different branch without messing with the working tree/index/HEAD pointer
```
rebase-- --stay -4r <upstream> <some-branch>
```
Assuming that you are not working on `<some-branch>` at the time, `rebase--` will behave just like
running `rebase-- <upstream> <some-branch>` _but_ without touching your working tree, index or
`HEAD` pointer. The rebase is attempted and the reference for `<some-branch>` will be moved if the
rebase succeeds (that is because the options `-4r` and `--stay` were used in the example).

## rebase _for real_ but do not move the branch reference and work on _detached HEAD_ instead
```
rebase-- --detach -4r <upstream> <some-branch>
```
In this case `rebase--` will run the rebase and, if it succeeds, it will checkout the commit id
product of the rebase, which will make you start working on a `detached HEAD`. The reference where
`HEAD` was before is not moved.


# main options

## --onto
The same way that `--onto` works in `git-rebase`, it provides a different point
to start piling up rebased commits instead of the tip of the `upstream` provided.

## --for-real/-4r
By default, `rebase--` does _not_ move the working tree around. It will run the
rebase calculation saving objects in the database and will report the final commit
out of the rebase process. If you want to let `rebase--` checkout to the final commit
(and adjust the reference if using a local branch), this option will do it. Consider that
if you are **not** using `--stay`, it will run a hard reset to the final commit of the rebase.

## --detach
If working using `--for-real/-4r`, you can ask git to switch to the final commit of the rebase
calculation on a `detached HEAD` without moving the local reference that `HEAD` was pointing to.

## --stay
If you want to rebase a local branch **different from the one you are currently working on**,
you can use `--for-real/-4r` together with this option so that the _other_ local reference is adjusted
after the rebase is done. The current working tree is not affected in any way if you use this option.

## --force/-f
Avoid checking the state of the working tree. Consider that when the rebase calculation is finished, a hard
reset to the final commit will take place if using `--for-real` without `--stay`. Needless to say that
you should use this option **with care**.

## --verbose
Provide more information about the objects that are involved in a conflict.

# Licensing / Copyright
Copyright (c) 2025 Edmundo Carmona Antoranz

Released under the terms of GPLv2.0
