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
