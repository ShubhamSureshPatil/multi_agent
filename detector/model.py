"""Toy detector: colour threshold + connected components.

To mimic a real anchor-based head, it emits several jittered candidate boxes
per object plus a few random low-score false positives. There is NO NMS yet,
so duplicates hurt precision.
"""
import numpy as np

from detector.data import CLASS_COLORS


def _components(mask):
    """4-connected components -> list of xyxy boxes."""
    h, w = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    boxes = []
    for y, x in zip(*np.nonzero(mask)):
        if seen[y, x]:
            continue
        stack, ys, xs = [(y, x)], [], []
        seen[y, x] = True
        while stack:
            cy, cx = stack.pop()
            ys.append(cy)
            xs.append(cx)
            for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    stack.append((ny, nx))
        if len(ys) >= 16:
            boxes.append([min(xs), min(ys), max(xs) + 1, max(ys) + 1])
    return boxes


def predict(img, seed: int = 0, candidates_per_object: int = 3, n_false_pos: int = 2):
    """Returns (boxes (N,4) float32, scores (N,), labels (N,))."""
    rng = np.random.default_rng(seed)
    boxes, scores, labels = [], [], []
    for cls, color in enumerate(CLASS_COLORS):
        mask = np.abs(img.astype(np.int16) - color).sum(-1) < 60
        for b in _components(mask):
            b = np.array(b, dtype=np.float32)
            size = b[2:] - b[:2]
            for k in range(candidates_per_object):
                jitter = rng.normal(0, 0.05 * k, size=4) * np.tile(size, 2)
                boxes.append(b + jitter)
                scores.append(0.9 - 0.08 * k + rng.normal(0, 0.08))
                labels.append(cls)
    h, w = img.shape[:2]
    for _ in range(n_false_pos):
        x0, y0 = rng.uniform(0, w - 20), rng.uniform(0, h - 20)
        boxes.append(np.array([x0, y0, x0 + 20, y0 + 20], dtype=np.float32))
        scores.append(rng.uniform(0.3, 0.85))
        labels.append(int(rng.integers(len(CLASS_COLORS))))
    if not boxes:
        return np.zeros((0, 4), np.float32), np.zeros(0, np.float32), np.zeros(0, np.int64)
    return (np.stack(boxes).astype(np.float32), np.array(scores, np.float32),
            np.array(labels, np.int64))
