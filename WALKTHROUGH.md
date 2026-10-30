# Live demo: 3 Claude agents, 1 CV repo, 3 features at once

**Repo:** a toy surface-defect detector (scratch / dent / stain), numpy only, with tests and eval that finish in under 2 s.
**Baseline:** `mAP@0.5 = 0.8475`. The model emits duplicate boxes because there is no NMS yet.

Tested with Claude Code v2.1.314 (terminal). The desktop-app steps are not tested, so click through them once before the talk.

---

## 0. Before the talk

```bash
cd /d/projects/friday_session/defect-detector
claude            # once: accept the "trust this folder" prompt, then /exit
./scripts/reset-demo.sh
```
- Background agents won't start in a folder that hasn't been trusted.
- `reset-demo.sh` removes agent worktrees and branches and resets `main` to the `demo-start` tag.
  It keeps `backup/*` branches. Clear old sessions from the list with `claude agents` → `claude rm <id>`.
  If `rm` refuses because of unpushed commits, it prints the exact `--discard-unpushed …` command to run.
- **Fallback:** `backup/mosaic-augmentation`, `backup/per-class-eval` and `backup/nms` hold finished work from a
  previous run. If agents stall live, merge those instead of the `worktree-*` branches.

---

## 1. The repo and the Claude config (≈4 min)

```bash
tree -a -I '.git|__pycache__|.pytest_cache|worktrees'
python3 -m pytest -q && python3 -m detector.eval
```

Walk through the `.claude/` folder. **This is the main idea of the talk**:

| File | What it is | Talking point |
|---|---|---|
| `CLAUDE.md` | Short: commands, layout, conventions | *Not* a big master spec. Every session loads it, so keep it lean. |
| `.claude/skills/add-augmentation/` | *How* we add an augmentation (box rules + required tests) | A skill is a **reusable procedure**, not a feature. It loads only when relevant. |
| `.claude/skills/run-eval/` | How we report mAP before/after | Same idea. Encodes team practice once. |
| `.claude/agents/cv-reviewer.md` | A reviewer subagent with CV-specific checks | A specialist with its own context and read-only tools. |
| `.claude/hooks/run-tests.sh` + `settings.json` | A **Stop hook**: an agent can't finish while tests are red | Enforced by the harness, not left to the model to remember. |
| `tickets/*.md` | The 3 features | Features are throwaway. They live in tickets or issues, **not** in skills. |

> Old way: a `main.md` plus one "skill file" per feature, one session working through them in order.
> New way: skills for *how*, tickets for *what*, **one agent per ticket in its own worktree**.

---

## 2. Launch 3 agents in parallel (≈3 min)

### Terminal
```bash
./scripts/launch-agents.sh
```
That runs one of these for each ticket (show the script):
```bash
claude --bg -w nms -n nms --permission-mode auto "Implement tickets/03-nms.md ..."
```
- `-w nms`: creates a **git worktree** in `.claude/worktrees/nms` on branch `worktree-nms`. Agents can't overwrite each other's files.
- `--bg`: runs in the background and returns your prompt immediately.
- `-n`: a readable name for `claude agents`, `logs` and `attach`.
- `--permission-mode auto`: routine commands are approved automatically. With `acceptEdits`, all 3 agents
  stopped at the first compound shell command (`… && for …`) and waited for approval.

**Show that they run in parallel:**
```bash
claude agents          # all 3 listed, all "working" at the same time
git worktree list      # 3 extra checkouts, one per agent, all from the same commit
watch -n 2 'for w in .claude/worktrees/*; do echo "== $w"; git -C $w status --short; done'
```

### GUI (what the team uses), not tested
Same concepts in the Claude desktop app → **Code**:
open the repo folder → start a **new session** for each ticket, with the session's **worktree** option on.
Each session shows up in the sidebar and you click between them. Paste the same prompt:
`Implement tickets/03-nms.md. Commit when tests pass and report mAP before -> after.`

---

## 3. While they work (≈3 min)

**They're fast:** in testing each agent finished in **0.7–1.0 min**. Start talking through this section as soon as
you launch them. Have `claude agents` open in a second pane.

```bash
claude logs nms                    # peek at an agent's terminal
claude attach mosaic-augmentation  # open it in this terminal (the conversation is kept after it finishes)
```
What to point out (seen in testing):
- The mosaic agent **loaded the `add-augmentation` skill** on its own. Its description matches the task, and it did this in every run.
- The NMS agent **used `run-eval`** for its before/after table in one of two runs. Skills are *offered*, not forced.
  If a step must always happen, use a hook (next point).
- **Stop hook:** it never had to fire in testing because agents ran the tests themselves. To show it, open
  `.claude/hooks/run-tests.sh` and explain: exit code 2 means "you can't stop yet" and pytest's output goes back to Claude.

**Plan mode** (needs a live session, so start a 4th ticket interactively):
```bash
claude -w score-threshold
```
Press `Shift+Tab` until the footer shows **plan mode**, then ask:
*"The confusion matrix shows ~250 background false positives. Add a score threshold to eval. Plan it first."*
Claude reads the code and proposes a plan. You approve it, and only then does it edit files.

---

## 4. Review and merge (≈6 min)

```bash
git branch                       # worktree-* = this run's agents, backup/* = fallback
```

**Review a branch with the subagent.** In a `claude` session on `main`:
```
Use the cv-reviewer agent to review the worktree-mosaic-augmentation branch.
```
or the built-in review: `/code-review worktree-mosaic-augmentation`.

**Merge:**
```bash
git merge worktree-mosaic-augmentation   # transforms.py + its tests
git merge worktree-nms                   # postprocess.py, eval.py
git merge worktree-per-class-eval        # metrics.py, ALSO eval.py → git auto-merged it in both test runs
```
Talking point: NMS and per-class-eval both edited `eval.py`, but in different places, so git merged them.
**Merging cleanly doesn't prove they work together.** Run the tests on the combined result. If you do get a
real conflict (agents can write different code each run), hand it to Claude:
```
Resolve the merge conflict in detector/eval.py so both NMS and the per-class report work. Run tests and eval.
```

**Final result** (in both test runs: all tests pass, 17–18 depending on what the agents wrote):
```bash
python3 -m pytest -q
python3 -m detector.eval             # mAP 0.8475 → 0.9922; per-class AP 0.989 / 0.995 / 0.994
python3 -m detector.eval --no-nms    # back to 0.8475: shows the gain came from NMS
```
**Finale:** the new confusion matrix shows **249 background false positives** at score ≥ 0.5
(the toy model emits 2 random boxes per image). The per-class-eval agent's report has found the *next* ticket,
which is the plan-mode session from section 3.

---

## 4b. Parallel vs single agent (≈2 min)

`./scripts/race.sh` starts the 3-agent team **and** one solo agent doing all 3 tickets in order, at the same
moment, each in its own worktree. It writes a scoreboard to `results/`. Recorded run (`results/race-20261030-092334.md`):

| | wall time | peak context | output tokens | result |
|---|---|---|---|---|
| Team of 3 (slowest agent) | **1.0 min** | 55.6k–59.1k per agent | 25.6k total | 3 branches; merged: 17 tests, mAP 0.9922 |
| Solo, sequential | **1.7 min** | 65.4k | 20.3k | 1 branch, 17 tests, mAP 0.9922 |

How to present it honestly:
- **Speed:** total time is the *slowest* ticket, not the *sum*. These toy tickets take under a minute, so it's
  1.7×. Longer, independent tickets get closer to N× for N agents. The limits are the slowest ticket and your rate limits.
- **Context:** every agent starts at about **41k tokens** (system prompt, tools, CLAUDE.md, skill list). On top of
  that, each team agent used 14.4k–18.1k for its ticket, and the solo agent used 24.3k, because it carries the earlier
  tickets' code and logs into the later ones. On real features that pile-up is what makes a long single session drift.
- **Cost:** the team produced about 25% *more* output tokens, and each agent re-reads the repo. You pay a bit
  more for less wall-clock time.
- **Quality:** the same on these toy tickets. Don't claim parallel writes better code.
- **Workflow:** 3 branches means you can review, merge or revert one feature without touching the others.
  The solo branch is all-or-nothing.

---

## 5. Takeaways (≈2 min)

1. **CLAUDE.md is short.** Commands, layout, conventions.
2. **Skills are *how*, tickets are *what*.** Don't make a skill per feature.
3. **One feature → one agent → one worktree → one branch.** Split work along module boundaries to keep conflicts rare.
4. **Hooks enforce, skills suggest.** Put "tests must pass" in a hook.
5. **Review with a specialist subagent** before merging.
6. Terminal and GUI are the **same model**: sessions plus worktrees. Use whichever you like.

---

## Cheat sheet

| Goal | Terminal | Desktop app (not tested) |
|---|---|---|
| New isolated agent | `claude -w <name>` | New session, worktree on |
| Background agent | `claude --bg -w <name> -n <name> "prompt"` | Start a session, switch away |
| See all agents | `claude agents` | Sidebar |
| Peek / jump in | `claude logs <name>` / `claude attach <name>` | Click the session |
| Remove a finished agent | `claude rm <id>` | — |
| Plan first | `Shift+Tab` until "plan mode" | Plan mode toggle |
| Review | `/code-review <branch>` or the `cv-reviewer` subagent | Same, in the prompt |
| Race team vs solo | `./scripts/race.sh` | — |
| Reset demo | `./scripts/reset-demo.sh` | — |
