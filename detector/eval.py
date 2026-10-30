"""Evaluate the toy detector on a synthetic validation split.

    python -m detector.eval --n 200
"""
import argparse

from detector.data import make_dataset
from detector.metrics import average_precision
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


if __name__ == "__main__":
    main()
