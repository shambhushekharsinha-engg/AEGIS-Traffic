# app/core/ucf_dataset_loader.py
"""
UCF Crime Dataset Loader
=========================
Dynamically scans the UCF Crime dataset directory and loads frame-level PNG
images for training and evaluation.

Dataset structure (partially extracted — loader handles whatever is available):
    dataset/archive (2)/
        Train/
            Abuse/        ← PNG frames: Abuse001_x264_0.png, _10.png, ...
            Arrest/
            Arson/
            Assault/
            Burglary/
            Explosion/
            Fighting/
            NormalVideos/
        Test/
            Abuse/
            ...
            RoadAccidents/ ← available in Test even if Train not fully extracted
            Robbery/
            Shooting/
            Shoplifting/
            Stealing/
            Vandalism/

Design:
- All scanning is lazy (no pre-loading of images)
- Gracefully handles categories with 0 images
- Supports deterministic sampling via a fixed random seed
"""

import os
import random
from pathlib import Path
from datetime import datetime
from typing import Optional


# ─── Default dataset root (relative to project root) ─────────────────────────
_DEFAULT_DATASET_BASE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "dataset",
    "archive (2)",
)

# Labels that map to "normal / safe" (not anomaly)
NORMAL_LABELS = {"NormalVideos", "Normal_Videos"}

# Severity mapping for each crime category
CRIME_SEVERITY = {
    "Abuse":         "HIGH",
    "Arrest":        "MEDIUM",
    "Arson":         "CRITICAL",
    "Assault":       "HIGH",
    "Burglary":      "HIGH",
    "Explosion":     "CRITICAL",
    "Fighting":      "HIGH",
    "NormalVideos":  "NONE",
    "RoadAccidents": "CRITICAL",
    "Robbery":       "HIGH",
    "Shooting":      "CRITICAL",
    "Shoplifting":   "LOW",
    "Stealing":      "MEDIUM",
    "Vandalism":     "MEDIUM",
}

# Map categories to AEGIS scenario strings
CRIME_TO_SCENARIO = {
    "Abuse":         "accident",
    "Arrest":        "normal",
    "Arson":         "emergency",
    "Assault":       "accident",
    "Burglary":      "accident",
    "Explosion":     "emergency",
    "Fighting":      "accident",
    "NormalVideos":  "normal",
    "RoadAccidents": "accident",
    "Robbery":       "accident",
    "Shooting":      "emergency",
    "Shoplifting":   "normal",
    "Stealing":      "normal",
    "Vandalism":     "congested",
}


class UCFDatasetLoader:
    """
    Dynamically discovers and loads UCF Crime Dataset frames.

    Args:
        dataset_base_path:  Root of the extracted archive. Defaults to
                            `<project_root>/dataset/archive (2)/`.
        seed:               Random seed for deterministic sampling.
    """

    def __init__(self, dataset_base_path: Optional[str] = None, seed: int = 42):
        self.base_path = Path(dataset_base_path or _DEFAULT_DATASET_BASE)
        self.train_root = self.base_path / "Train"
        self.test_root  = self.base_path / "Test"
        self.seed = seed

    # ── Public API ─────────────────────────────────────────────────────────────

    def get_dataset_status(self) -> dict:
        """
        Returns a status report of what is currently available on disk.
        Safe to call even when extraction is still ongoing.
        """
        train_stats = self._scan_split(self.train_root)
        test_stats  = self._scan_split(self.test_root)

        total_train_frames = sum(s["frame_count"] for s in train_stats.values())
        total_test_frames  = sum(s["frame_count"] for s in test_stats.values())

        all_categories = sorted(set(train_stats) | set(test_stats))

        return {
            "dataset_base": str(self.base_path),
            "base_exists":  self.base_path.exists(),
            "train": {
                "root":        str(self.train_root),
                "exists":      self.train_root.exists(),
                "categories":  len(train_stats),
                "total_frames": total_train_frames,
                "breakdown":   train_stats,
            },
            "test": {
                "root":        str(self.test_root),
                "exists":      self.test_root.exists(),
                "categories":  len(test_stats),
                "total_frames": total_test_frames,
                "breakdown":   test_stats,
            },
            "all_known_categories": all_categories,
            "extraction_complete": (len(all_categories) == 14),
            "scanned_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        }

    def load_train_data(
        self, max_per_class: int = 200, shuffle: bool = True
    ) -> tuple[list[str], list[str]]:
        """
        Returns (image_paths, labels) for the training split.

        Args:
            max_per_class:  Maximum number of frames to sample per class.
            shuffle:        If True, shuffle the result before returning.

        Returns:
            Tuple of (list[str] paths, list[str] label_names)
        """
        return self._load_split(self.train_root, max_per_class, shuffle)

    def load_test_data(
        self, max_per_class: int = 50, shuffle: bool = False
    ) -> tuple[list[str], list[str]]:
        """Returns (image_paths, labels) for the test split."""
        return self._load_split(self.test_root, max_per_class, shuffle)

    def load_all_data(
        self,
        max_train_per_class: int = 200,
        max_test_per_class: int = 50,
        balanced_binary: bool = False,
    ) -> dict:
        """
        Convenience method: loads both splits and returns a dict.

        Args:
            max_train_per_class:  Max frames per category in train split.
            max_test_per_class:   Max frames per category in test split.
            balanced_binary:      If True, cap Anomalous training frames to
                                  match the Normal frame count (1:1 balance).
                                  Prevents class imbalance in binary mode.
        """
        train_paths, train_labels = self.load_train_data(max_train_per_class)
        test_paths,  test_labels  = self.load_test_data(max_test_per_class)

        # Optional: balance Anomalous ↔ Normal for binary training
        if balanced_binary:
            rng = random.Random(self.seed)
            normal_idx   = [i for i, l in enumerate(train_labels) if l in NORMAL_LABELS]
            anomaly_idx  = [i for i, l in enumerate(train_labels) if l not in NORMAL_LABELS]
            target_n     = len(normal_idx)  # match Normal count
            if len(anomaly_idx) > target_n:
                anomaly_idx = rng.sample(anomaly_idx, target_n)
            keep_idx = sorted(normal_idx + anomaly_idx)
            train_paths  = [train_paths[i]  for i in keep_idx]
            train_labels = [train_labels[i] for i in keep_idx]

        all_classes = sorted(set(train_labels) | set(test_labels))

        return {
            "train_paths":  train_paths,
            "train_labels": train_labels,
            "test_paths":   test_paths,
            "test_labels":  test_labels,
            "classes":      all_classes,
            "n_classes":    len(all_classes),
            "n_train":      len(train_paths),
            "n_test":       len(test_paths),
        }

    def get_available_classes(self) -> list[str]:
        """Returns all class names found across both splits (sorted)."""
        train_classes = set(self._scan_split(self.train_root).keys())
        test_classes  = set(self._scan_split(self.test_root).keys())
        return sorted(train_classes | test_classes)

    def is_anomaly(self, label: str) -> bool:
        """Returns True if this label is a crime/anomaly (not NormalVideos)."""
        return label not in NORMAL_LABELS

    def get_crime_severity(self, label: str) -> str:
        """Returns severity string for the given category label."""
        return CRIME_SEVERITY.get(label, "UNKNOWN")

    def get_scenario_for_label(self, label: str) -> str:
        """Maps a crime category to an AEGIS scenario string."""
        return CRIME_TO_SCENARIO.get(label, "normal")

    # ── Internal helpers ───────────────────────────────────────────────────────

    def _scan_split(self, split_root: Path) -> dict:
        """Scans a split directory and returns per-category stats."""
        stats = {}
        if not split_root.exists():
            return stats

        for category_dir in sorted(split_root.iterdir()):
            if not category_dir.is_dir():
                continue
            png_files = list(category_dir.glob("*.png"))
            stats[category_dir.name] = {
                "path":        str(category_dir),
                "frame_count": len(png_files),
                "is_anomaly":  self.is_anomaly(category_dir.name),
                "severity":    self.get_crime_severity(category_dir.name),
                "aegis_scenario": self.get_scenario_for_label(category_dir.name),
            }
        return stats

    def _load_split(
        self, split_root: Path, max_per_class: int, shuffle: bool
    ) -> tuple[list[str], list[str]]:
        """Core loader: returns (paths, labels) with sampling."""
        rng = random.Random(self.seed)
        all_paths:  list[str] = []
        all_labels: list[str] = []

        if not split_root.exists():
            return all_paths, all_labels

        for category_dir in sorted(split_root.iterdir()):
            if not category_dir.is_dir():
                continue
            label = category_dir.name
            png_files = [str(p) for p in sorted(category_dir.glob("*.png"))]
            if not png_files:
                continue

            # Sample up to max_per_class frames deterministically
            if len(png_files) > max_per_class:
                sampled = rng.sample(png_files, max_per_class)
            else:
                sampled = png_files

            all_paths.extend(sampled)
            all_labels.extend([label] * len(sampled))

        if shuffle:
            combined = list(zip(all_paths, all_labels))
            rng.shuffle(combined)
            if combined:
                all_paths, all_labels = zip(*combined)
                all_paths  = list(all_paths)
                all_labels = list(all_labels)

        return all_paths, all_labels
