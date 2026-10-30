# Live demo: 3 Claude agents, 1 CV repo, 3 features at once

**Repo:** a toy surface-defect detector (scratch / dent / stain), numpy only, with tests and eval that finish in under 2 s.
**Baseline:** `mAP@0.5 = 0.8475`. The model emits duplicate boxes because there is no NMS yet.

---

## 0. One-time setup (do this before the talk)

```bash
cd /d/projects/friday_session/defect-detector
claude            # accept the "trust this folder" prompt, then /exit
```
Background agents won't start in a folder that hasn't been trusted.

**Pre-bake a fallback:** run the whole demo once the night before, then
`git branch backup/<name> <agent-branch>` for each finished branch.
If anything stalls live, merge the backup branches instead.
Run `./scripts/reset-demo.sh` to go back to the clean starting point.

---

## 1. The repo and the Claude config (≈4 min)

```bash
tree -a -I '.git|__pycache__|.pytest_cache'
python3 -m pytest -q && python3 -m detector.eval
```

Walk through the `.claude/` folder. **This is the main idea of the talk**:

| File | What it is | Talking point |
|---|---|---|
| `CLAUDE.md` | Short: commands, layout, conventions | *Not* a big master spec. Every session loads it, so keep it lean. |
| `.claude/skills/add-augmentation/` | *How* we add an augmentation (box rules + required tests) | A skill is a **reusable procedure**, not a feature. It loads only when relevant. |
| `.claude/skills/run-eval/` | How we report mAP before/after | Same idea. Encodes team practice once. |
| `.claude/agents/cv-reviewer.md` | A reviewer subagent with CV-specific checks | A specialist with its own context and limited tools. |
| `.claude/hooks/run-tests.sh` + `settings.json` | A **Stop hook**: an agent can't finish while tests are red | Enforced by the harness, not left to the model to remember. |
| `tickets/*.md` | The 3 features | Features are throwaway. They live in tickets or issues, **not** in skills. |

> Old way: a `main.md` plus one "skill file" per feature, one session working through them in order.
> New way: skills for *how*, tickets for *what*, **one agent per ticket in its own worktree**.

---

## 2. Launch 3 agents in parallel (≈2 min)

### Terminal
```bash
./scripts/launch-agents.sh
```
That runs one of these for each ticket (show the script):
```bash
claude --bg -w nms -n nms --permission-mode acceptEdits "Implement tickets/03-nms.md ..."
```
- `-w nms`: creates a **git worktree** (its own folder and branch). Agents can't overwrite each other's files.
- `--bg`: runs in the background and returns your prompt immediately.
- `-n`: a readable name for the agent list.

```bash
claude agents          # dashboard of running agents
git worktree list      # 3 extra checkouts, one per agent
```

### GUI (what the team uses)
Same concepts in the Claude desktop app → **Code**:
open the repo folder → start a **new session** for each ticket, with the session's **worktree** option on.
Each session shows up in the sidebar and you click between them. Paste the same prompt:
`Implement tickets/03-nms.md. Commit when tests pass and report mAP before -> after.`

---

## 3. While they work (≈6 min)

```bash
claude logs nms        # peek without interrupting
claude attach mosaic   # jump into a live session (approve a prompt, steer it)
```
Things to point out as they happen:
- The mosaic agent **picks up the `add-augmentation` skill** on its own, because its description matches the task.
- The NMS agent **uses `run-eval`** and reports a before/after table.
- If an agent tries to finish with failing tests, the **Stop hook blocks it** and it goes back to fix them.
- **Plan mode**, live in one session: attach to `per-class-eval`, press `Shift+Tab` twice for plan mode,
  and ask *"also add per-class precision/recall, plan it first"*. Claude proposes a plan, you approve it, then it writes code.

---

## 4. Review and merge (≈6 min)

```bash
git branch                       # see the 3 agent branches
```

**Review one branch with the subagent.** In a normal `claude` session on `main`:
```
Use the cv-reviewer agent to review the mosaic branch against main.
```
or use the built-in review: `/code-review` from inside that worktree.

**Merge:**
```bash
git merge <mosaic-branch>        # touches transforms.py only → clean
git merge <nms-branch>           # touches eval.py
git merge <per-class-eval-branch># ALSO touches eval.py → likely conflict
```
The conflict is **on purpose**. Two features that edit the same CLI is a real, everyday situation. Fix it in Claude:
```
Resolve the merge conflict in detector/eval.py so both NMS and the per-class report work. Run tests and eval.
```

**Final result:**
```bash
python3 -m pytest -q
python3 -m detector.eval         # mAP ≈ 0.99 (from 0.8475), plus per-class table + confusion matrix
```

---

## 5. Takeaways (≈2 min)

1. **CLAUDE.md is short.** Commands, layout, conventions.
2. **Skills are *how*, tickets are *what*.** Don't make a skill per feature.
3. **One feature → one agent → one worktree → one branch.** Split work along module boundaries to keep conflicts rare.
4. **Hooks enforce, prompts suggest.** Put "tests must pass" in a hook.
5. **Review with a specialist subagent** before merging.
6. Terminal and GUI are the **same model**: sessions plus worktrees. Use whichever you like.

---

## Cheat sheet

| Goal | Terminal | Desktop app |
|---|---|---|
| New isolated agent | `claude -w <name>` | New session, worktree on |
| Background agent | `claude --bg -w <name> "prompt"` | Start a session, switch away |
| See all agents | `claude agents` | Sidebar |
| Peek / jump in | `claude logs <name>` / `claude attach <name>` | Click the session |
| Plan first | `Shift+Tab` → plan mode | Plan mode toggle |
| Review | `/code-review` or the `cv-reviewer` subagent | Same, in the prompt |
| Reset demo | `./scripts/reset-demo.sh` | — |
