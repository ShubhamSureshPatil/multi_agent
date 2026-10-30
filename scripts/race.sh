#!/usr/bin/env bash
# Race: 3 parallel agents (one ticket each) vs 1 agent doing all 3 tickets in sequence.
# All 4 start at the same moment, each in its own worktree. Writes results/race-<time>.md
#   ./scripts/race.sh
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
mkdir -p results
stamp=$(date +%Y%m%d-%H%M%S)
ids="results/.race-$stamp.ids"
: > "$ids"

start=$(date +%s)
echo "start: $(date +%T)"

# Team of 3: one agent per ticket.
./scripts/launch-agents.sh | tee /dev/stderr | grep -oE 'backgrounded · [0-9a-f]+ · [^ ]+' \
  | awk '{print $3, $5}' >> "$ids"

# Solo agent: same tickets, one after another.
claude --bg -w solo -n solo --permission-mode auto \
  "Implement tickets/01-mosaic-augmentation.md, then tickets/02-per-class-eval.md, then tickets/03-nms.md, \
one at a time in that order. Read CLAUDE.md first and use the project skills where they apply. \
After each ticket, run the tests and commit. At the end, summarise what you changed and the mAP before -> after." \
  | tee /dev/stderr | grep -oE 'backgrounded · [0-9a-f]+ · [^ ]+' | awk '{print $3, $5}' >> "$ids"

echo; echo "racing… (claude agents to watch)"
python3 scripts/race_report.py "$ids" "$start" "results/race-$stamp.md"
