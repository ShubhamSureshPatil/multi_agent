#!/usr/bin/env bash
# Stop hook: an agent may not finish while tests are red.
# Exit 2 = block the stop and feed stderr back to Claude.
input=$(cat)
# Don't loop forever if we already blocked once this turn.
if echo "$input" | grep -q '"stop_hook_active": *true'; then exit 0; fi
cwd=$(echo "$input" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("cwd","."))')
cd "$cwd" || exit 0
if ! out=$(python3 -m pytest -q 2>&1); then
  echo "Tests are failing — fix them before finishing:" >&2
  echo "$out" | tail -25 >&2
  exit 2
fi
exit 0
