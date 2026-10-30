import numpy as np

from detector.metrics import average_precision, box_iou


def test_iou_identical_and_disjoint():
    a = np.array([[0, 0, 10, 10]], np.float32)
    b = np.array([[0, 0, 10, 10], [20, 20, 30, 30]], np.float32)
    assert np.allclose(box_iou(a, b), [[1.0, 0.0]], atol=1e-6)


def test_perfect_predictions_give_ap_1():
    gb = np.array([[0, 0, 10, 10], [20, 20, 30, 30]], np.float32)
    gl = np.array([0, 1])
    preds = [(gb, np.array([0.9, 0.8]), gl)]
    assert average_precision(preds, [(gb, gl)]) > 0.999


def test_wrong_class_is_false_positive():
    gb = np.array([[0, 0, 10, 10]], np.float32)
    preds = [(gb, np.array([0.9]), np.array([1]))]
    assert average_precision(preds, [(gb, np.array([0]))]) == 0.0
