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
- no interactive mode. (**It could be a feature!!!** Take your pick).
- it does not allow (currently) to start working on the updated working tree
if there is a conflict.


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
