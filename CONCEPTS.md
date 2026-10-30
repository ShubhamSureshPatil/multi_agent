# Parallel Claude agents for CV work

One repo, one agent per feature, each in its own worktree. Skills say **how** we work, tickets say **what** to build.

---

## 1. Old way vs new way

```mermaid
flowchart LR
  subgraph OLD["Old: one session, in sequence"]
    direction TB
    M[main.md<br/>big master spec] --> S1[skill: feature A]
    S1 --> S2[skill: feature B]
    S2 --> S3[skill: feature C]
    S3 --> B1[one branch,<br/>all-or-nothing]
  end
  subgraph NEW["New: one agent per ticket, in parallel"]
    direction TB
    C[CLAUDE.md<br/>short] --> A1[agent A<br/>worktree A]
    C --> A2[agent B<br/>worktree B]
    C --> A3[agent C<br/>worktree C]
    A1 --> R[review + merge<br/>per branch]
    A2 --> R
    A3 --> R
  end
```

| | Old | New |
|---|---|---|
| Spec | One big master file | Short `CLAUDE.md` + one ticket per feature |
| Skills | One per feature | One per **repeatable procedure** |
| Execution | One session, one feature after another | N sessions, each in its own worktree |
| Rules | "Please run tests" in a prompt | A **hook** enforces it |

---

## 2. What goes where

```mermaid
flowchart TB
  R[(repo)] --> CM["CLAUDE.md<br/>commands · layout · conventions"]
  R --> SK[".claude/skills/<br/>HOW: run-eval, add-augmentation"]
  R --> AG[".claude/agents/<br/>specialists: cv-reviewer"]
  R --> HK[".claude/settings.json hooks<br/>RULES: tests must pass"]
  R --> TK["tickets/<br/>WHAT: mosaic, per-class eval, NMS"]
  CM -. loaded by every session .-> X((agent))
  SK -. loaded when relevant .-> X
  HK -. runs automatically .-> X
  TK -. given in the prompt .-> X
```

| Piece | Lives for | Example |
|---|---|---|
| `CLAUDE.md` | Life of the repo | `python3 -m detector.eval` prints mAP |
| Skill | Life of the repo | "Mosaic/crop must clip boxes and drop labels too" |
| Subagent | Life of the repo | `cv-reviewer` checks box/pixel geometry and NMS bugs |
| Hook | Life of the repo | Stop hook: can't finish while pytest is red |
| Ticket | One feature | `tickets/03-nms.md` |

---

## 3. The workflow

```mermaid
flowchart LR
  T1[ticket 01<br/>mosaic] --> W1["claude --bg -w mosaic-augmentation"]
  T2[ticket 02<br/>per-class eval] --> W2["claude --bg -w per-class-eval"]
  T3[ticket 03<br/>NMS] --> W3["claude --bg -w nms"]
  W1 --> H{Stop hook<br/>tests green?}
  W2 --> H
  W3 --> H
  H -- no --> FIX[agent keeps fixing]
  FIX --> H
  H -- yes --> RV[cv-reviewer /<br/>code-review]
  RV --> MG[git merge<br/>per branch]
  MG --> TS[pytest + eval<br/>on merged main]
```

```bash
./scripts/launch-agents.sh            # 3 background agents, 3 worktrees
claude agents                         # watch them
claude attach nms                     # jump in
git merge worktree-nms                # merge one feature at a time
```

**Isolation:** each agent edits its own copy of the repo on its own branch. Overlaps (here, `eval.py`) only meet at merge time.

```mermaid
gitGraph
  commit id: "demo-start"
  branch worktree-mosaic-augmentation
  commit id: "mosaic aug"
  checkout main
  branch worktree-per-class-eval
  commit id: "per-class AP"
  checkout main
  branch worktree-nms
  commit id: "NMS"
  checkout main
  merge worktree-mosaic-augmentation
  merge worktree-nms
  merge worktree-per-class-eval
```

---

## 4. Results: team of 3 vs one solo agent

Same 3 tickets, all four agents started at the same moment (`./scripts/race.sh`).

**Timeline (seconds).** Total time is the slowest ticket, not the sum:

```mermaid
gantt
  title Wall-clock time (approx., from 0.7 / 0.8 / 1.0 / 1.7 min)
  dateFormat X
  axisFormat %M:%S
  section Team of 3
  mosaic          :0, 42
  per-class eval  :0, 48
  NMS             :0, 60
  section Solo
  all 3 tickets in sequence :0, 102
```

```mermaid
xychart-beta
  title "Wall time (minutes)"
  x-axis ["Team of 3 (slowest)", "Solo"]
  y-axis "minutes" 0 --> 2
  bar [1.0, 1.7]
```

**Context.** Every agent starts at about 41k tokens. This is what each one added while working:

```mermaid
xychart-beta
  title "Context added by the work (k tokens)"
  x-axis ["mosaic", "per-class", "NMS", "Solo (all 3)"]
  y-axis "k tokens" 0 --> 30
  bar [14.4, 14.6, 18.1, 24.3]
```

**Outcome.** Same quality on the merged result:

```mermaid
xychart-beta
  title "mAP@0.5"
  x-axis ["Baseline", "Team (merged)", "Solo"]
  y-axis "mAP" 0.8 --> 1.0
  bar [0.8475, 0.9922, 0.9922]
```

| | Team of 3 | Solo |
|---|---|---|
| Wall time | **1.0 min** | 1.7 min |
| Peak context per agent | 56–59k | 65k |
| Output tokens | 25.6k | **20.3k** |
| Tests / mAP | 17 / 0.9922 | 17 / 0.9922 |
| Revert one feature | One branch | Pick it out of a single branch |

**Takeaway:** parallel buys **wall-clock time** and **smaller, focused context** for about 25% more output tokens.
On toy tickets that's 1.7×; for N independent features the time gets closer to N×.

---

## 5. When to use what

```mermaid
flowchart TD
  Q{What are you doing?} -->|Repeat it across features| SK[Write a skill]
  Q -->|Must always happen| HK[Add a hook]
  Q -->|Needs a specialist view| AG[Add a subagent]
  Q -->|A new feature| P{Independent of<br/>other work?}
  P -->|yes| WT["New agent + worktree<br/>claude -w name"]
  P -->|no, same files| SEQ[Same session,<br/>plan mode first]
```

## Rules of thumb

1. Keep `CLAUDE.md` short. Every session pays for it.
2. A skill is a procedure, not a feature.
3. One feature → one agent → one worktree → one branch.
4. Split tickets along module boundaries (`transforms.py`, `metrics.py`, `postprocess.py`) to avoid conflicts.
5. Hooks enforce rules, prompts only suggest them.
6. A clean merge isn't proof. Run tests and eval on the merged result.
