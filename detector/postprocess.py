"""Detection post-processing."""
import numpy as np

from detector.metrics import box_iou


def nms(boxes, scores, labels, iou_thr: float = 0.5):
    """Per-class greedy non-maximum suppression.

    Keeps the highest-scoring box and drops any same-class box whose IoU with
    it exceeds iou_thr, then repeats. Boxes of different classes never
    suppress each other. Returns the filtered (boxes, scores, labels), sorted
    by descending score.
    """
    order = np.argsort(-scores, kind="stable")
    keep = []
    for cls in np.unique(labels):
        idx = order[labels[order] == cls]
        while len(idx):
            best, rest = idx[0], idx[1:]
            keep.append(best)
            ious = box_iou(boxes[best:best + 1], boxes[rest])[0]
            idx = rest[ious <= iou_thr]
    keep = np.array(sorted(keep, key=lambda i: -scores[i]), dtype=np.int64)
    return boxes[keep], scores[keep], labels[keep]
