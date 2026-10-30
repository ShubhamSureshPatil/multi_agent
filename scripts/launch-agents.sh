#!/usr/bin/env bash
# Launch one background Claude agent per ticket, each in its own git worktree.
#   ./scripts/launch-agents.sh            # all three tickets
#   ./scripts/launch-agents.sh 03-nms     # just one
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

tickets=("$@")
[ ${#tickets[@]} -eq 0 ] && tickets=(01-mosaic-augmentation 02-per-class-eval 03-nms)

for t in "${tickets[@]}"; do
  name="${t#*-}"   # 01-mosaic-augmentation -> mosaic-augmentation
  echo "▶ launching agent '$name' for tickets/$t.md"
  claude --bg -w "$name" -n "$name" --permission-mode auto \
    "Implement tickets/$t.md. Read CLAUDE.md first and use the project skills where they apply. \
When tests pass, commit your work on this branch with a clear message, then summarise what you changed \
and the mAP before -> after."
done

echo
echo "Watch them:   claude agents"
echo "Peek at one:  claude logs <name>      Jump in:  claude attach <name>"
