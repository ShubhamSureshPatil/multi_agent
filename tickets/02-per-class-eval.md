# 02 — Per-class AP and confusion matrix

The eval only prints one mAP number. The team needs to know *which* defect class is weak.

- Add `per_class_ap(preds, gts, n_classes, iou_thr=0.5) -> list[float]` to `detector/metrics.py`
  (reuse `average_precision` by filtering to one class).
- Add `confusion_matrix(preds, gts, n_classes, iou_thr=0.5, score_thr=0.5)` with an extra
  "background" row/column for missed GTs and false positives.
- `python3 -m detector.eval` additionally prints a per-class AP table and the confusion matrix
  using class names from `detector.CLASSES`.

Done when: tests cover a perfect-prediction case and a one-misclassification case.
Files: `detector/metrics.py`, `detector/eval.py`, `tests/test_metrics.py`.
