#!/usr/bin/env bash
# Put the repo back to the pre-demo state: remove agent worktrees + branches, reset main.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
main_wt=$(pwd)
git worktree list --porcelain | awk '/^worktree /{print $2}' | while read -r wt; do
  [ "$wt" = "$main_wt" ] || { echo "removing worktree $wt"; git worktree remove --force "$wt"; }
done
git worktree prune
git checkout -q main
git reset -q --hard demo-start
git branch --format='%(refname:short)' | grep -vE '^(main|backup/.*)$' | xargs -r git branch -D
echo "reset to demo-start. Background sessions (if any): claude agents  → stop with: claude stop <id>"
