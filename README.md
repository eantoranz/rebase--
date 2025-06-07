# rebase--

The basic rebasing tool.

# What is rebase--

`rebase--` tries to be a simple rebase tool that
deals with only the most basic rebasing scenarios
while also trying to overcome the simplest of 
conflicts.

It is not intended to become a replacement of `git-rebase`.

# features (intended)
- rebase history, including merges
- avoid conflicts **if possible** based on what the commits being rebased did originally.
- no interactive mode
- work without moving the working tree

# Licensing / Copyright
Copyright (c) 2025 Edmundo Carmona Antoranz
Released under the terms of GPLv2.0
