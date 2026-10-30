"""Evaluate the toy detector on a synthetic validation split.

    python -m detector.eval --n 200
"""
import argparse

from detector import CLASSES
from detector.data import make_dataset
from detector.metrics import average_precision, confusion_matrix, per_class_ap
from detector.model import predict


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200, help="number of val images")
    ap.add_argument("--seed", type=int, default=123)
    args = ap.parse_args()

    data = make_dataset(args.n, seed=args.seed)
    preds = [predict(img, seed=i) for i, (img, _, _) in enumerate(data)]
    gts = [(boxes, labels) for _, boxes, labels in data]
    print(f"images: {len(data)}")
    print(f"mAP@0.5: {average_precision(preds, gts):.4f}")

    print("\nper-class AP@0.5:")
    for name, cap in zip(CLASSES, per_class_ap(preds, gts, len(CLASSES))):
        print(f"  {name:<10} {cap:.4f}")

    cm = confusion_matrix(preds, gts, len(CLASSES))
    names = list(CLASSES) + ["background"]
    w = max(len(n) for n in names) + 2
    print("\nconfusion matrix (rows = GT, cols = pred, score >= 0.5):")
    print(" " * w + "".join(f"{n:>{w}}" for n in names))
    for name, row in zip(names, cm):
        print(f"{name:<{w}}" + "".join(f"{v:>{w}d}" for v in row))


if __name__ == "__main__":
    main()
