"""Detection metrics."""
import numpy as np


def box_iou(a, b):
    """Pairwise IoU between (N,4) and (M,4) xyxy boxes -> (N, M)."""
    tl = np.maximum(a[:, None, :2], b[None, :, :2])
    br = np.minimum(a[:, None, 2:], b[None, :, 2:])
    inter = (br - tl).clip(min=0).prod(-1)
    area_a = (a[:, 2:] - a[:, :2]).prod(-1)
    area_b = (b[:, 2:] - b[:, :2]).prod(-1)
    return inter / (area_a[:, None] + area_b[None, :] - inter + 1e-9)


def average_precision(preds, gts, iou_thr: float = 0.5):
    """Class-agnostic AP over a dataset.

    preds: list of (boxes, scores, labels) per image
    gts:   list of (boxes, labels) per image
    A prediction is a true positive if it matches an unmatched GT of the same
    class with IoU >= iou_thr.
    """
    records, n_gt = [], 0
    for img_id, ((pb, ps, pl), (gb, gl)) in enumerate(zip(preds, gts)):
        n_gt += len(gb)
        for i in range(len(pb)):
            records.append((ps[i], img_id, i))
    records.sort(key=lambda r: -r[0])
    matched = [np.zeros(len(gb), bool) for gb, _ in gts]
    tp = np.zeros(len(records))
    for k, (_, img_id, i) in enumerate(records):
        pb, _, pl = preds[img_id]
        gb, gl = gts[img_id]
        if len(gb) == 0:
            continue
        ious = box_iou(pb[i:i + 1], gb)[0]
        ious[(gl != pl[i]) | matched[img_id]] = 0
        j = int(ious.argmax())
        if ious[j] >= iou_thr:
            matched[img_id][j] = True
            tp[k] = 1
    if n_gt == 0:
        return 0.0
    ctp = np.cumsum(tp)
    recall = ctp / n_gt
    precision = ctp / np.arange(1, len(tp) + 1)
    # all-point interpolation (VOC style)
    mrec = np.concatenate([[0], recall, [1]])
    mpre = np.concatenate([[0], precision, [0]])
    mpre = np.maximum.accumulate(mpre[::-1])[::-1]
    idx = np.nonzero(mrec[1:] != mrec[:-1])[0]
    return float(((mrec[idx + 1] - mrec[idx]) * mpre[idx + 1]).sum())


def per_class_ap(preds, gts, n_classes: int, iou_thr: float = 0.5):
    """AP for each class, computed by filtering preds and GTs to that class.

    Classes with no ground truth get nan (AP is undefined there).
    """
    aps = []
    for c in range(n_classes):
        cp = [(pb[pl == c], ps[pl == c], pl[pl == c]) for pb, ps, pl in preds]
        cg = [(gb[gl == c], gl[gl == c]) for gb, gl in gts]
        if sum(len(gl) for _, gl in cg) == 0:
            aps.append(float("nan"))
        else:
            aps.append(average_precision(cp, cg, iou_thr))
    return aps


def confusion_matrix(preds, gts, n_classes: int, iou_thr: float = 0.5,
                     score_thr: float = 0.5):
    """(n_classes+1, n_classes+1) matrix; rows = GT class, cols = predicted class.

    Index n_classes is "background": row bg counts false positives (predictions
    matching no GT), column bg counts missed GTs. Predictions with
    score >= score_thr are matched greedily in score order to the unmatched GT
    with the highest IoU >= iou_thr, regardless of class.
    """
    bg = n_classes
    cm = np.zeros((n_classes + 1, n_classes + 1), np.int64)
    for (pb, ps, pl), (gb, gl) in zip(preds, gts):
        keep = np.nonzero(ps >= score_thr)[0]
        order = keep[np.argsort(-ps[keep], kind="stable")]
        matched = np.zeros(len(gb), bool)
        for i in order:
            if len(gb):
                ious = box_iou(pb[i:i + 1], gb)[0]
                ious[matched] = 0
                j = int(ious.argmax())
                if ious[j] >= iou_thr:
                    matched[j] = True
                    cm[gl[j], pl[i]] += 1
                    continue
            cm[bg, pl[i]] += 1
        for j in np.nonzero(~matched)[0]:
            cm[gl[j], bg] += 1
    return cm
