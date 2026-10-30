---
name: add-augmentation
description: How to add a new data augmentation to detector/transforms.py correctly, including box handling and the required tests. Use whenever adding or changing an augmentation.
---

# Add an augmentation

Signature: `def name(img, boxes, labels, rng: np.random.Generator, ...) -> (img, boxes, labels)`

Rules that bite in detection (check every one):
- Transform the boxes with exactly the same geometry as the pixels.
- Clip boxes to the output image bounds.
- Drop boxes that became degenerate (width or height <= 2 px) **and drop their labels too**.
- Never modify inputs in place — copy.
- Output dtype: img uint8, boxes float32, labels int64.

Required tests in `tests/test_transforms.py`:
1. All boxes are inside the output image.
2. `len(boxes) == len(labels)`.
3. A pixel-level check: the pixels inside an output box match the class colour
   (`detector.data.CLASS_COLORS[label]`) for most of the box area.

Finish by running `python3 -m pytest -q`.
