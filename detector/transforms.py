"""Data augmentations. Every transform takes and returns (img, boxes, labels)."""
import numpy as np


def hflip(img, boxes, labels):
    w = img.shape[1]
    out = boxes.copy()
    out[:, [0, 2]] = w - boxes[:, [2, 0]]
    return img[:, ::-1].copy(), out, labels


def random_crop(img, boxes, labels, rng: np.random.Generator, min_scale: float = 0.6):
    h, w = img.shape[:2]
    s = rng.uniform(min_scale, 1.0)
    ch, cw = int(h * s), int(w * s)
    y0, x0 = rng.integers(0, h - ch + 1), rng.integers(0, w - cw + 1)
    out = boxes.copy()
    out[:, [0, 2]] = (out[:, [0, 2]] - x0).clip(0, cw)
    out[:, [1, 3]] = (out[:, [1, 3]] - y0).clip(0, ch)
    keep = (out[:, 2] - out[:, 0] > 2) & (out[:, 3] - out[:, 1] > 2)
    return img[y0:y0 + ch, x0:x0 + cw].copy(), out[keep], labels[keep]


def mosaic(samples, rng: np.random.Generator, out_size: int = 128):
    """YOLO-style mosaic: tile 4 (img, boxes, labels) samples around a random centre."""
    assert len(samples) == 4, "mosaic needs exactly 4 samples"
    cx = int(rng.integers(out_size // 4, 3 * out_size // 4 + 1))
    cy = int(rng.integers(out_size // 4, 3 * out_size // 4 + 1))
    # Quadrant regions on the canvas: (x0, y0, x1, y1) for TL, TR, BL, BR.
    regions = [(0, 0, cx, cy), (cx, 0, out_size, cy),
               (0, cy, cx, out_size), (cx, cy, out_size, out_size)]
    canvas = np.full((out_size, out_size, 3), 128, dtype=np.uint8)
    all_boxes, all_labels = [], []
    for (img, boxes, labels), (rx0, ry0, rx1, ry1) in zip(samples, regions):
        h, w = img.shape[:2]
        ch, cw = min(ry1 - ry0, h), min(rx1 - rx0, w)
        sy, sx = rng.integers(0, h - ch + 1), rng.integers(0, w - cw + 1)
        canvas[ry0:ry0 + ch, rx0:rx0 + cw] = img[sy:sy + ch, sx:sx + cw]
        out = boxes.astype(np.float32, copy=True)
        # Same shift as the pixels, then clip to the pasted area (not just the canvas)
        # so boxes never spill into a neighbouring quadrant.
        out[:, [0, 2]] = (out[:, [0, 2]] - sx + rx0).clip(rx0, rx0 + cw)
        out[:, [1, 3]] = (out[:, [1, 3]] - sy + ry0).clip(ry0, ry0 + ch)
        keep = (out[:, 2] - out[:, 0] > 2) & (out[:, 3] - out[:, 1] > 2)
        all_boxes.append(out[keep])
        all_labels.append(labels[keep])
    boxes = np.concatenate(all_boxes).astype(np.float32).reshape(-1, 4)
    labels = np.concatenate(all_labels).astype(np.int64)
    return canvas, boxes, labels
