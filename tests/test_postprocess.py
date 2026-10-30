import numpy as np

from detector.postprocess import nms


def test_overlapping_same_class_boxes_collapse():
    boxes = np.array([[0, 0, 10, 10], [1, 1, 11, 11], [0, 0, 10, 11]], np.float32)
    scores = np.array([0.7, 0.9, 0.8], np.float32)
    labels = np.array([0, 0, 0], np.int64)
    b, s, l = nms(boxes, scores, labels)
    assert len(b) == 1
    assert np.allclose(b[0], boxes[1]) and s[0] == np.float32(0.9) and l[0] == 0


def test_different_classes_do_not_suppress():
    boxes = np.array([[0, 0, 10, 10], [0, 0, 10, 10]], np.float32)
    scores = np.array([0.9, 0.8], np.float32)
    labels = np.array([0, 1], np.int64)
    b, s, l = nms(boxes, scores, labels)
    assert len(b) == 2
    assert sorted(l.tolist()) == [0, 1]


def test_disjoint_boxes_kept_and_threshold_respected():
    boxes = np.array([[0, 0, 10, 10], [20, 20, 30, 30], [0, 0, 10, 15]], np.float32)
    scores = np.array([0.9, 0.5, 0.8], np.float32)
    labels = np.zeros(3, np.int64)
    # IoU(box0, box2) = 100/150 ~= 0.67
    assert len(nms(boxes, scores, labels, iou_thr=0.5)[0]) == 2
    assert len(nms(boxes, scores, labels, iou_thr=0.7)[0]) == 3


def test_empty_input():
    b, s, l = nms(np.zeros((0, 4), np.float32), np.zeros(0, np.float32), np.zeros(0, np.int64))
    assert b.shape == (0, 4) and s.shape == (0,) and l.shape == (0,)
