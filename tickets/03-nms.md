# 03 — Non-maximum suppression

The toy model emits ~3 overlapping candidates per defect and we never run NMS, so
duplicates count as false positives. mAP@0.5 baseline: 0.8475.

- New module `detector/postprocess.py` with `nms(boxes, scores, labels, iou_thr=0.5)`,
  **per-class**, numpy only, returns the filtered `(boxes, scores, labels)`.
- Apply it in `detector/eval.py` behind a flag `--iou-thr` (default 0.5; `--no-nms` disables).
- Sweep iou_thr in {0.3, 0.5, 0.7} and report mAP for each in your final message.

Done when: tests for NMS (overlapping same-class boxes collapse, different classes don't) pass
and mAP improves. Use the `run-eval` skill to report before/after.
Files: `detector/postprocess.py`, `detector/eval.py`, `tests/test_postprocess.py`.
