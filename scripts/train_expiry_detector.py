from __future__ import annotations

import argparse
import math
import os
import random
import shutil
from datetime import datetime, timedelta
from pathlib import Path

import cv2
import numpy as np

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")

ROOT = Path(__file__).resolve().parents[1]
YOLO_CONFIG_PARENT = ROOT / ".ultralytics"
YOLO_CONFIG_PARENT.mkdir(exist_ok=True)
os.environ.setdefault("YOLO_CONFIG_DIR", str(YOLO_CONFIG_PARENT))


def _rotate_points(points: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    ones = np.ones((points.shape[0], 1), dtype=np.float32)
    homogenous = np.hstack([points.astype(np.float32), ones])
    return homogenous @ matrix.T


def _bbox_from_points(points: np.ndarray, width: int, height: int, pad: int = 10) -> tuple[int, int, int, int]:
    x1 = max(0, int(np.floor(points[:, 0].min())) - pad)
    y1 = max(0, int(np.floor(points[:, 1].min())) - pad)
    x2 = min(width - 1, int(np.ceil(points[:, 0].max())) + pad)
    y2 = min(height - 1, int(np.ceil(points[:, 1].max())) + pad)
    return x1, y1, x2, y2


def _write_yolo_label(label_path: Path, box: tuple[int, int, int, int], width: int, height: int) -> None:
    x1, y1, x2, y2 = box
    xc = ((x1 + x2) / 2) / width
    yc = ((y1 + y2) / 2) / height
    bw = (x2 - x1) / width
    bh = (y2 - y1) / height
    label_path.write_text(f"0 {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}\n", encoding="utf-8")


def _make_one_image(path: Path, label_path: Path, rng: random.Random) -> None:
    width, height = 640, 416
    bg_color = tuple(rng.randint(205, 255) for _ in range(3))
    image = np.full((height, width, 3), bg_color, dtype=np.uint8)
    noise = np.random.default_rng(rng.randint(0, 2**32 - 1)).integers(0, 40, image.shape, dtype=np.uint8)
    image = cv2.add(image, noise)

    fonts = [
        cv2.FONT_HERSHEY_SIMPLEX,
        cv2.FONT_HERSHEY_COMPLEX,
        cv2.FONT_HERSHEY_DUPLEX,
        cv2.FONT_HERSHEY_TRIPLEX,
    ]
    prefixes = ["EXP:", "Expiry:", "Use by:", "Best Before:", "BB:", "BBD:", ""]
    formats = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%Y", "%d %b %Y", "%Y/%m/%d"]

    exp_date = datetime.now() + timedelta(days=rng.randint(-120, 260))
    full_text = f"{rng.choice(prefixes)} {exp_date.strftime(rng.choice(formats))}".strip()
    font = rng.choice(fonts)
    font_scale = rng.uniform(0.75, 1.35)
    thickness = rng.randint(2, 3)
    text_color = tuple(rng.randint(0, 45) for _ in range(3))

    (tw, th), baseline = cv2.getTextSize(full_text, font, font_scale, thickness)
    x = rng.randint(24, max(25, width - tw - 45))
    y = rng.randint(130, height - 85)

    cv2.putText(image, "NET WT: 500g", (x, max(35, y - 55)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    cv2.putText(image, full_text, (x, y), font, font_scale, text_color, thickness)
    cv2.putText(image, "Batch: A1X9", (x, min(height - 25, y + 55)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    text_box = np.array(
        [
            [x, y - th - baseline],
            [x + tw, y - th - baseline],
            [x + tw, y + baseline],
            [x, y + baseline],
        ],
        dtype=np.float32,
    )

    angle = rng.uniform(-12, 12)
    matrix = cv2.getRotationMatrix2D((width / 2, height / 2), angle, 1.0)
    rotated = cv2.warpAffine(image, matrix, (width, height), borderValue=bg_color)
    rotated_box = _rotate_points(text_box, matrix)
    box = _bbox_from_points(rotated_box, width, height)

    cv2.imwrite(str(path), rotated)
    _write_yolo_label(label_path, box, width, height)


def build_dataset(output_dir: Path, train_count: int, val_count: int, seed: int) -> Path:
    rng = random.Random(seed)
    if output_dir.exists():
        shutil.rmtree(output_dir)

    for split in ("train", "val"):
        (output_dir / "images" / split).mkdir(parents=True, exist_ok=True)
        (output_dir / "labels" / split).mkdir(parents=True, exist_ok=True)

    for split, count in (("train", train_count), ("val", val_count)):
        for idx in range(count):
            image_path = output_dir / "images" / split / f"expiry_{idx:04d}.jpg"
            label_path = output_dir / "labels" / split / f"expiry_{idx:04d}.txt"
            _make_one_image(image_path, label_path, rng)

    data_yaml = output_dir / "data.yaml"
    data_yaml.write_text(
        "\n".join(
            [
                f"path: {output_dir.as_posix()}",
                "train: images/train",
                "val: images/val",
                "names:",
                "  0: expiry_date_region",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return data_yaml


def train_detector(data_yaml: Path, epochs: int, imgsz: int, batch: int) -> Path:
    from ultralytics import YOLO

    runs_dir = ROOT / "runs" / "expiry_detector"
    model = YOLO("yolov8n.yaml")
    result = model.train(
        data=str(data_yaml),
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        workers=0,
        device="cpu",
        project=str(runs_dir),
        name="train",
        exist_ok=True,
        verbose=False,
    )

    best = Path(result.save_dir) / "weights" / "best.pt"
    if not best.exists():
        raise FileNotFoundError(f"YOLO training completed but best weights were not found: {best}")

    model_dir = ROOT / "models"
    model_dir.mkdir(exist_ok=True)
    target = model_dir / "expiry_detector.pt"
    shutil.copy2(best, target)
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the local YOLO expiry date-region detector.")
    parser.add_argument("--train-count", type=int, default=180)
    parser.add_argument("--val-count", type=int, default=40)
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--imgsz", type=int, default=320)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--seed", type=int, default=412)
    args = parser.parse_args()

    data_yaml = build_dataset(ROOT / "data" / "expiry_detector", args.train_count, args.val_count, args.seed)
    target = train_detector(data_yaml, args.epochs, args.imgsz, args.batch)
    print(f"Saved trained YOLO expiry detector to {target}")


if __name__ == "__main__":
    main()
