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
