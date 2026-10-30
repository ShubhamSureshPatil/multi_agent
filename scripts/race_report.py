"""Wait for the race agents to finish, then write a scoreboard.

    python3 scripts/race_report.py <ids-file> <start-epoch> <out.md>

ids-file lines: "<session-id-prefix> <name>" as printed by `claude --bg`.
"""
import glob
import json
import os
import subprocess
import sys
import time

ids_file, start, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
agents = dict(line.split() for line in open(ids_file) if line.strip())  # id -> name
finished, blocked_seen = {}, set()

while len(finished) < len(agents):
    sessions = json.loads(subprocess.check_output(["claude", "agents", "--json", "--all"]))
    by_id = {s.get("id"): s for s in sessions if s.get("id")}
    for aid, name in agents.items():
        s = by_id.get(aid, {})
        if s.get("state") == "blocked" and aid not in blocked_seen:
            blocked_seen.add(aid)
            print(f"  ! {name} is blocked waiting for input: claude attach {aid}", flush=True)
        if aid not in finished and s.get("state") == "done":
            finished[aid] = time.time() - start
            print(f"  ✓ {name} finished after {finished[aid] / 60:.1f} min", flush=True)
    time.sleep(5)


def transcript_stats(aid):
    """Peak context size and total output tokens from the session transcript."""
    paths = glob.glob(os.path.expanduser(f"~/.claude/projects/*/{aid}*.jsonl"))
    peak = out_tok = turns = 0
    for path in paths:
        for line in open(path):
            try:
                msg = json.loads(line).get("message") or {}
            except json.JSONDecodeError:
                continue
            u = msg.get("usage") if isinstance(msg, dict) else None
            if not u:
                continue
            ctx = (u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0)
                   + u.get("cache_creation_input_tokens", 0))
            peak = max(peak, ctx)
            out_tok += u.get("output_tokens", 0)
            turns += 1
    return peak, out_tok, turns


def branch_stats(name):
    wt = f".claude/worktrees/{name}"
    commits = subprocess.run(["git", "-C", wt, "rev-list", "--count", "main..HEAD"],
                             capture_output=True, text=True).stdout.strip()
    tests = subprocess.run(["python3", "-m", "pytest", "-q"], cwd=wt,
                           capture_output=True, text=True).stdout.strip().splitlines()[-1:]
    evalout = subprocess.run(["python3", "-m", "detector.eval"], cwd=wt,
                             capture_output=True, text=True).stdout
    m = next((l.split()[-1] for l in evalout.splitlines() if l.startswith("mAP")), "?")
    return commits, (tests[0] if tests else "?"), m


rows = []
for aid, name in agents.items():
    peak, out_tok, turns = transcript_stats(aid)
    commits, tests, m = branch_stats(name)
    rows.append((name, finished[aid] / 60, peak, out_tok, turns, commits, tests, m))

team = [r for r in rows if r[0] != "solo"]
solo = [r for r in rows if r[0] == "solo"]
lines = ["# Race: 3 parallel agents vs 1 sequential agent", "",
         "| agent | wall time (min) | peak context (tokens) | output tokens | model calls | commits | tests | mAP@0.5 on branch |",
         "|---|---|---|---|---|---|---|---|"]
for r in rows:
    lines.append(f"| {r[0]} | {r[1]:.1f} | {r[2]:,} | {r[3]:,} | {r[4]} | {r[5]} | {r[6]} | {r[7]} |")
if team and solo:
    t_team, t_solo = max(r[1] for r in team), solo[0][1]
    lines += ["",
              f"**Team of 3 done in {t_team:.1f} min** (slowest agent) vs **solo {t_solo:.1f} min** "
              f"→ {t_solo / t_team:.1f}× faster.",
              f"Largest team context: {max(r[2] for r in team):,} tokens vs solo: {solo[0][2]:,} tokens."]
open(out, "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
print(f"\nsaved {out}")
