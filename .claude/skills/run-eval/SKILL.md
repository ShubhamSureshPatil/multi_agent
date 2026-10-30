---
name: run-eval
description: Run the detector evaluation and report mAP before/after a change. Use after any change to model, postprocessing, metrics or data code, or when asked "how good is the model".
---

# Run eval

1. Get the baseline on the base branch without switching branches:
   `git stash -q && python3 -m detector.eval --n 200; git stash pop -q`
   (skip if there are no uncommitted changes — just run it once).
2. Run `python3 -m detector.eval --n 200` on the current code.
3. Report as a small table:

   | metric | before | after |
   |---|---|---|
   | mAP@0.5 | ... | ... |

4. If mAP dropped by more than 0.01, say so loudly and explain why before finishing.
