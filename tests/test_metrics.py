import numpy as np

from detector.metrics import average_precision, box_iou, confusion_matrix, per_class_ap


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


def test_per_class_ap_perfect():
    gb = np.array([[0, 0, 10, 10], [20, 20, 30, 30]], np.float32)
    gl = np.array([0, 1])
    preds = [(gb, np.array([0.9, 0.8]), gl)]
    aps = per_class_ap(preds, [(gb, gl)], n_classes=3)
    assert aps[0] > 0.999 and aps[1] > 0.999
    assert np.isnan(aps[2])  # no GT for class 2


def test_per_class_ap_one_misclassification():
    gb = np.array([[0, 0, 10, 10], [20, 20, 30, 30]], np.float32)
    gl = np.array([0, 1])
    preds = [(gb, np.array([0.9, 0.8]), np.array([0, 0]))]  # class-1 GT predicted as 0
    aps = per_class_ap(preds, [(gb, gl)], n_classes=2)
    assert aps[0] > 0.999  # TP at rank 1 reaches full recall before the FP
    assert aps[1] == 0.0


def test_confusion_matrix_perfect():
    gb = np.array([[0, 0, 10, 10], [20, 20, 30, 30]], np.float32)
    gl = np.array([0, 1])
    preds = [(gb, np.array([0.9, 0.8]), gl)]
    cm = confusion_matrix(preds, [(gb, gl)], n_classes=2)
    assert (cm == np.diag([1, 1, 0])).all()


def test_confusion_matrix_one_misclassification():
    gb = np.array([[0, 0, 10, 10], [20, 20, 30, 30]], np.float32)
    gl = np.array([0, 1])
    preds = [(gb, np.array([0.9, 0.8]), np.array([0, 0]))]
    cm = confusion_matrix(preds, [(gb, gl)], n_classes=2)
    expected = np.zeros((3, 3), np.int64)
    expected[0, 0] = 1
    expected[1, 0] = 1  # GT class 1 predicted as class 0
    assert (cm == expected).all()


def test_confusion_matrix_background():
    gb = np.array([[0, 0, 10, 10]], np.float32)
    gl = np.array([0])
    pb = np.array([[50, 50, 60, 60], [0, 0, 10, 10]], np.float32)
    preds = [(pb, np.array([0.9, 0.1]), np.array([1, 0]))]  # FP + low-score hit
    cm = confusion_matrix(preds, [(gb, gl)], n_classes=2)
    assert cm[2, 1] == 1  # false positive -> background row
    assert cm[0, 2] == 1  # GT missed (its match is below score_thr)
    assert cm.sum() == 2
