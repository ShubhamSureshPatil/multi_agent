# 01 — Mosaic augmentation

Add `mosaic(samples, rng, out_size=128)` to `detector/transforms.py`.

- Takes a list of 4 `(img, boxes, labels)` samples and tiles them into one
  `out_size x out_size` image around a random centre point (YOLO-style mosaic).
- Each quadrant is a crop of its source image; boxes are shifted, clipped, and
  degenerate ones dropped together with their labels.
- Follow the `add-augmentation` skill for the rules and required tests.

Done when: tests pass, including a pixel-level test that boxes still land on the defect colour.
Files: `detector/transforms.py`, `tests/test_transforms.py`.
