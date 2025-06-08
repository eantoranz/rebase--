# rebase--

The basic rebasing tool.

# What is rebase--

`rebase--` tries to be a simple rebase tool that
deals with only the most basic rebasing scenarios
while also trying to overcome the simplest of 
conflicts.

It is not intended to become a replacement of `git-rebase`.

# features
- rebase history, including merges
- avoid conflicts **if possible** based on what the commits being rebased did originally.
- no interactive mode.
- work without moving the working tree.
- **Optionally** Move to the final commit of the rebase.
- can move local references without moving the working tree / `HEAD`.

# main options

## --onto
The same way that `--onto` works in `git-rebase`, it provides a different point
to start piling up rebased commits instead of the tip of the `upstream` provided.

## --for-real/4r
By default, `rebase--` does _not_ move the working tree around. It will run the
rebase calculation saving objects in the database and will report the final commit
out of the rebase process. If you want to let `rebase--` checkout to the final commit
(and adjust the reference if using a local branch), this option will do it. Consider that
if you are **not** using `--stay`, it will run a hard reset to the final commit of the rebase.

## --stay
If you want to rebase a local branch **different from the one you are currently working on**,
you can use `--for-real/-4r` together with this option so that the _other_ local reference is adjusted
after the rebase is done. The current working tree is not affected in any way if you use this option.

## --force
Avoid checking the state of the working tree. Consider that when the rebase calculation is finished, a hard
reset to the final commit will take place if using `--for-real` without `--stay`. Needless to say that
you should use this option **with care**.

# Licensing / Copyright
Copyright (c) 2025 Edmundo Carmona Antoranz
Released under the terms of GPLv2.0
