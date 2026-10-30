"""Synthetic defect dataset: grey noisy 'metal' plates with coloured defects.

Boxes are float arrays of shape (N, 4) in xyxy pixel coords, labels are int (N,).
"""
import numpy as np

from detector import CLASSES

IMG_SIZE = 128
# One RGB colour per class so the toy detector can find them.
CLASS_COLORS = np.array([[220, 40, 40], [40, 200, 40], [40, 60, 220]], dtype=np.uint8)


def make_sample(rng: np.random.Generator, max_objects: int = 4):
    img = rng.normal(128, 12, size=(IMG_SIZE, IMG_SIZE, 3)).clip(0, 255).astype(np.uint8)
    boxes, labels = [], []
    for _ in range(rng.integers(1, max_objects + 1)):
        w, h = rng.integers(8, 32, size=2)
        x0, y0 = rng.integers(0, IMG_SIZE - w), rng.integers(0, IMG_SIZE - h)
        box = np.array([x0, y0, x0 + w, y0 + h], dtype=np.float32)
        if boxes and _max_iou(box, np.stack(boxes)) > 0.0:
            continue  # keep defects non-overlapping for a clean toy problem
        cls = int(rng.integers(len(CLASSES)))
        img[y0:y0 + h, x0:x0 + w] = CLASS_COLORS[cls]
        boxes.append(box)
        labels.append(cls)
    return img, np.stack(boxes), np.array(labels, dtype=np.int64)


def make_dataset(n: int, seed: int = 0):
    rng = np.random.default_rng(seed)
    return [make_sample(rng) for _ in range(n)]


def _max_iou(box, boxes):
    from detector.metrics import box_iou
    return float(box_iou(box[None], boxes).max())
