import numpy as np

from detector.data import CLASS_COLORS, make_sample
from detector.transforms import hflip, mosaic, random_crop


def test_hflip_twice_is_identity():
    img, boxes, labels = make_sample(np.random.default_rng(0))
    img2, boxes2, _ = hflip(*hflip(img, boxes, labels))
    assert np.array_equal(img, img2)
    assert np.allclose(boxes, boxes2)


def test_random_crop_keeps_boxes_inside():
    rng = np.random.default_rng(1)
    for _ in range(20):
        img, boxes, labels = random_crop(*make_sample(rng), rng=rng)
        h, w = img.shape[:2]
        assert (boxes[:, [0, 2]] >= 0).all() and (boxes[:, [0, 2]] <= w).all()
        assert (boxes[:, [1, 3]] >= 0).all() and (boxes[:, [1, 3]] <= h).all()
        assert len(boxes) == len(labels)


def _mosaic_runs(n=30):
    rng = np.random.default_rng(2)
    for _ in range(n):
        samples = [make_sample(rng) for _ in range(4)]
        yield samples, mosaic(samples, rng=rng)


def test_mosaic_shapes_and_dtypes():
    for samples, (img, boxes, labels) in _mosaic_runs():
        assert img.shape == (128, 128, 3) and img.dtype == np.uint8
        assert boxes.dtype == np.float32 and boxes.shape[1] == 4
        assert labels.dtype == np.int64
        assert len(boxes) == len(labels)


def test_mosaic_keeps_boxes_inside_and_non_degenerate():
    for _, (img, boxes, _) in _mosaic_runs():
        h, w = img.shape[:2]
        assert (boxes[:, [0, 2]] >= 0).all() and (boxes[:, [0, 2]] <= w).all()
        assert (boxes[:, [1, 3]] >= 0).all() and (boxes[:, [1, 3]] <= h).all()
        assert (boxes[:, 2] - boxes[:, 0] > 2).all() and (boxes[:, 3] - boxes[:, 1] > 2).all()


def test_mosaic_does_not_modify_inputs():
    rng = np.random.default_rng(3)
    samples = [make_sample(rng) for _ in range(4)]
    copies = [(i.copy(), b.copy(), l.copy()) for i, b, l in samples]
    mosaic(samples, rng=rng)
    for (i, b, l), (i2, b2, l2) in zip(samples, copies):
        assert np.array_equal(i, i2) and np.array_equal(b, b2) and np.array_equal(l, l2)


def test_mosaic_boxes_land_on_class_colour():
    checked = 0
    for _, (img, boxes, labels) in _mosaic_runs():
        for box, label in zip(boxes.astype(int), labels):
            x0, y0, x1, y1 = box
            patch = img[y0:y1, x0:x1].reshape(-1, 3)
            match = (patch == CLASS_COLORS[label]).all(axis=1).mean()
            assert match > 0.9, (box, label, match)
            checked += 1
    assert checked > 50
