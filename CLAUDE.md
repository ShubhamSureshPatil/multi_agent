# defect-detector

Toy surface-defect detector (scratch / dent / stain) used to demo parallel Claude agents.
Pure numpy — no GPU, no torch. Everything runs in < 2 s.

## Commands
- Tests: `python3 -m pytest -q`
- Eval:  `python3 -m detector.eval --n 200`   (prints mAP@0.5; baseline is 0.8475)

## Layout
- `detector/data.py`       synthetic dataset; boxes are float32 xyxy pixels, labels int64
- `detector/transforms.py` augmentations, signature `(img, boxes, labels, ...) -> (img, boxes, labels)`
- `detector/model.py`      toy detector, returns `(boxes, scores, labels)`; emits duplicates (no NMS)
- `detector/metrics.py`    IoU + VOC-style AP
- `detector/eval.py`       eval CLI
- `tickets/`               feature tickets, one per agent

## Conventions
- numpy only; no new dependencies.
- Every new transform or metric gets a test in `tests/`.
- Report any mAP change in the final message: before -> after.
- Stay inside the files your ticket names; if you must touch `eval.py`, keep the change small.
