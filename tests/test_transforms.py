import numpy as np

from detector.data import make_sample
from detector.transforms import hflip, random_crop


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
