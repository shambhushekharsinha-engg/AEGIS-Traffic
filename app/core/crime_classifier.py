# app/core/crime_classifier.py
"""
UCF Crime Frame Classifier
===========================
Trains a HOG + SGDClassifier pipeline on the UCF Crime Dataset frames.

Design:
- Feature extraction: HOG (Histogram of Oriented Gradients) via scikit-image
  → Works entirely on CPU, no GPU required
  → 128×128 frame → HOG → 1764-dim feature vector
- Classifier: SGDClassifier (LinearSVC-like, incremental, fast)
  → Training on 200 frames/class for 8 classes takes ~60–90 seconds
- Model saved to data/ucf_crime_model.pkl via joblib

Public API:
    CrimeClassifier()
        .train(max_per_class=200) → TrainResult dict
        .predict_frame(path_or_array) → PredictionResult dict
        .predict_frame_b64(base64_str) → PredictionResult dict
        .get_model_info() → ModelInfo dict
        .is_model_available() → bool
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

from app.core.ucf_dataset_loader import (
    UCFDatasetLoader,
)

logger = logging.getLogger("crime_classifier")

# ── Optional heavy imports ────────────────────────────────────────────────────
try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    np = None
    NUMPY_AVAILABLE = False

try:
    import cv2

    CV2_AVAILABLE = True
except ImportError:
    cv2 = None
    CV2_AVAILABLE = False

try:
    from skimage.feature import hog

    SKIMAGE_AVAILABLE = True
except ImportError:
    hog = None
    SKIMAGE_AVAILABLE = False

try:
    import joblib
    from sklearn.linear_model import SGDClassifier
    from sklearn.metrics import accuracy_score, classification_report
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import LabelEncoder, StandardScaler

    SKLEARN_AVAILABLE = True
except ImportError:
    SGDClassifier = StandardScaler = LabelEncoder = Pipeline = None
    accuracy_score = classification_report = joblib = None
    SKLEARN_AVAILABLE = False

# Check if PIL is available as a fallback image loader
try:
    from PIL import Image

    PIL_AVAILABLE = True
except ImportError:
    Image = None
    PIL_AVAILABLE = False


# ── Paths ─────────────────────────────────────────────────────────────────────
_PROJECT_ROOT = Path(__file__).parent.parent.parent
_MODEL_PATH = _PROJECT_ROOT / "data" / "ucf_crime_model.pkl"
_META_PATH = _PROJECT_ROOT / "data" / "ucf_crime_meta.json"

# ── HOG config ────────────────────────────────────────────────────────────────
_FRAME_SIZE = (128, 128)  # resize target
_HOG_PIXELS = (16, 16)  # pixels_per_cell
_HOG_CELLS = (2, 2)  # cells_per_block
_HOG_ORIENT = 9  # orientations


# ── Helpers ───────────────────────────────────────────────────────────────────


def _ml_available() -> bool:
    return (
        NUMPY_AVAILABLE
        and SKLEARN_AVAILABLE
        and (CV2_AVAILABLE or PIL_AVAILABLE)
        and SKIMAGE_AVAILABLE
    )


def _load_image_gray(path: str) -> Optional["np.ndarray"]:
    """Load an image and return it as a grayscale 128x128 numpy array."""
    if CV2_AVAILABLE and cv2 is not None:
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return None
        return cv2.resize(img, _FRAME_SIZE)
    elif PIL_AVAILABLE and Image is not None:
        try:
            img = Image.open(path).convert("L").resize(_FRAME_SIZE)
            return np.array(img)
        except Exception:
            return None
    return None


def _load_image_color(path: str) -> Optional["np.ndarray"]:
    """Load an image and return it as a color 128x128 numpy array (BGR)."""
    if CV2_AVAILABLE and cv2 is not None:
        img = cv2.imread(path, cv2.IMREAD_COLOR)
        if img is None:
            return None
        return cv2.resize(img, _FRAME_SIZE)
    elif PIL_AVAILABLE and Image is not None:
        try:
            img = Image.open(path).convert("RGB").resize(_FRAME_SIZE)
            return np.array(img)[:, :, ::-1]  # RGB to BGR for consistency
        except Exception:
            return None
    return None


def _extract_color_histogram(
    img_bgr: "np.ndarray", bins: int = 32
) -> Optional["np.ndarray"]:
    """
    Extract a concatenated HSV colour histogram (3 channels x bins) from a BGR image.
    Provides luminance + colour distribution cues to complement HOG edge features.
    """
    if not CV2_AVAILABLE or cv2 is None:
        return None
    try:
        img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        hists = []
        for ch in range(3):
            hist = cv2.calcHist([img_hsv], [ch], None, [bins], [0, 256])
            hist = hist.flatten()
            total = hist.sum()
            if total > 0:
                hist = hist / total
            hists.append(hist)
        return np.concatenate(hists).astype(np.float32)  # 3*bins = 96-dim
    except Exception:
        return None


def _extract_hog(img: "np.ndarray") -> Optional["np.ndarray"]:
    """Extract HOG feature vector from a grayscale image."""
    if not SKIMAGE_AVAILABLE or hog is None:
        return None
    try:
        features = hog(
            img,
            orientations=_HOG_ORIENT,
            pixels_per_cell=_HOG_PIXELS,
            cells_per_block=_HOG_CELLS,
            block_norm="L2-Hys",
            feature_vector=True,
        )
        return features
    except Exception as e:
        logger.warning(f"HOG extraction failed: {e}")
        return None


def _extract_features(path: str) -> Optional["np.ndarray"]:
    """
    Full feature vector for a single image path:
      HOG (1764-dim) + colour histogram (96-dim) = 1860-dim total.
    Falls back to HOG-only when cv2 color reading is unavailable.
    """
    # Greyscale for HOG
    img_gray = _load_image_gray(path)
    if img_gray is None:
        return None
    hog_feat = _extract_hog(img_gray)
    if hog_feat is None:
        return None

    # Colour histogram (optional enrichment)
    img_color = _load_image_color(path)
    if img_color is not None:
        color_feat = _extract_color_histogram(img_color)
        if color_feat is not None:
            return np.concatenate([hog_feat, color_feat]).astype(np.float32)

    return hog_feat.astype(np.float32)


def _extract_features_batch(
    paths: list[str], labels: list[str], verbose: bool = True
) -> tuple[list, list]:
    """Loads images, extracts HOG + colour histogram features, returns (X, y) lists."""
    X, y = [], []
    total = len(paths)
    skipped = 0

    for i, (path, label) in enumerate(zip(paths, labels)):
        if verbose and i % 500 == 0:
            pct = i / total * 100
            print(f"  [Feature] Extracting... {i}/{total} ({pct:.0f}%)")

        feat = _extract_features(path)
        if feat is None:
            skipped += 1
            continue

        X.append(feat)
        y.append(label)

    if verbose:
        dim = len(X[0]) if X else 0
        print(
            f"  [Feature] Done. {len(X)} vectors ({dim}-dim), skipped {skipped} bad frames."
        )
    return X, y


# ── Main class ────────────────────────────────────────────────────────────────


class CrimeClassifier:
    """
    HOG + SGDClassifier-based crime detection model for UCF Crime frames.

    Usage:
        clf = CrimeClassifier()
        clf.train()                            # train from dataset
        result = clf.predict_frame("path.png") # predict single frame
    """

    def __init__(self, dataset_base_path: Optional[str] = None):
        self.loader = UCFDatasetLoader(dataset_base_path)
        self.pipeline: Optional[Pipeline] = None
        self.label_encoder: Optional[LabelEncoder] = None
        self.classes_: list[str] = []
        self._meta: dict = {}
        self._load_model_if_exists()

    # ── Training ───────────────────────────────────────────────────────────────

    def train(
        self,
        max_per_class: int = 200,
        verbose: bool = True,
        binary_mode: bool = True,
    ) -> dict:
        """
        Trains the crime anomaly detector on available UCF Crime training data.

        Strategy — Binary Anomaly Detection (default):
          The UCF Crime dataset uses video-level train/test splits, meaning
          frames from the same clip are never in both splits. This makes
          fine-grained 14-class classification extremely hard (test acc ~10%).

          Binary mode trains Normal (NormalVideos) vs Anomalous (all crime
          categories pooled) — which is:
            - Tractable with HOG features
            - Directly useful for AEGIS (is this scene a crime? yes/no)
            - Correctly framed for the dataset's anomaly-detection design

          After predicting binary anomaly, the predicted crime_category is
          determined by the scene context (scenario mapping) rather than
          per-frame fine-grained classification.

        Args:
            max_per_class:  Max frames per class to use (default 200).
            verbose:        Print progress to stdout.
            binary_mode:    If True, train Normal vs Anomalous (recommended).

        Returns:
            dict with training results and metrics.
        """
        if not _ml_available():
            return {
                "success": False,
                "error": "Missing dependencies. Install: scikit-learn scikit-image opencv-python-headless",
                "dependencies_missing": True,
            }

        mode_label = (
            "BINARY (Normal vs Anomalous)"
            if binary_mode
            else "MULTICLASS (14 categories)"
        )
        print(f"[UCF Classifier] Starting training pipeline... Mode: {mode_label}")
        t0 = time.time()

        # ── 1. Load data ──────────────────────────────────────────────────────
        data = self.loader.load_all_data(
            max_train_per_class=max_per_class,
            max_test_per_class=max(50, max_per_class // 4),
            balanced_binary=False,  # class_weight='balanced' in SGD handles imbalance
        )
        if data["n_train"] == 0:
            return {
                "success": False,
                "error": "No training data found. Check dataset path.",
                "n_train": 0,
            }

        if verbose:
            print(
                f"[Data] Loaded {data['n_train']} train frames, {data['n_test']} test frames"
            )
            print(f"       Classes: {data['classes']}")

        # ── 2. Remap labels for binary mode ───────────────────────────────────
        if binary_mode:
            train_labels = [
                "Normal" if self.loader.is_anomaly(length) is False else "Anomalous"
                for length in data["train_labels"]
            ]
            test_labels = [
                "Normal" if self.loader.is_anomaly(length) is False else "Anomalous"
                for length in data["test_labels"]
            ]
            if verbose:
                normal_n = train_labels.count("Normal")
                anomaly_n = train_labels.count("Anomalous")
                print(
                    f"[Binary] Normal: {normal_n} frames, Anomalous: {anomaly_n} frames"
                )
        else:
            train_labels = data["train_labels"]
            test_labels = data["test_labels"]

        # ── 3. Feature extraction ─────────────────────────────────────────────
        print("[HOG+Colour] Extracting features from training frames...")
        X_train_raw, y_train = _extract_features_batch(
            data["train_paths"], train_labels, verbose=verbose  # use remapped labels
        )

        if not X_train_raw:
            return {
                "success": False,
                "error": "Feature extraction failed for all training frames.",
            }

        X_train = np.array(X_train_raw, dtype=np.float32)

        # ── 4. Encode labels ──────────────────────────────────────────────────
        self.label_encoder = LabelEncoder()
        y_encoded = self.label_encoder.fit_transform(y_train)
        self.classes_ = list(self.label_encoder.classes_)

        # ── 5. Build & train pipeline ─────────────────────────────────────────
        print("[Train] Fitting SGDClassifier (LinearSVM) ...")
        self.pipeline = Pipeline(
            [
                ("scaler", StandardScaler()),
                (
                    "classifier",
                    SGDClassifier(
                        loss="hinge",  # LinearSVM
                        alpha=0.0001,
                        max_iter=1000,
                        tol=1e-3,
                        random_state=42,
                        class_weight="balanced",
                        n_jobs=-1,
                    ),
                ),
            ]
        )
        self.pipeline.fit(X_train, y_encoded)
        t_train = time.time() - t0

        # ── 6. Evaluate on test set ───────────────────────────────────────────
        train_acc = None
        test_acc = None
        report = {}

        try:
            train_pred = self.pipeline.predict(X_train)
            train_acc = round(float(accuracy_score(y_encoded, train_pred)), 4)
        except Exception:
            pass

        if data["n_test"] > 0:
            print("[Eval] Evaluating on test set...")
            X_test_raw, y_test = _extract_features_batch(
                data["test_paths"],
                test_labels,
                verbose=verbose,  # use remapped test labels
            )
            if X_test_raw:
                X_test = np.array(X_test_raw, dtype=np.float32)
                y_test_enc = self.label_encoder.transform(
                    [length for length in y_test if length in self.classes_]
                )
                # Filter test set to only known classes
                valid_idx = [
                    i for i, length in enumerate(y_test) if length in self.classes_
                ]
                X_test_valid = X_test[valid_idx]
                y_test_valid = y_test_enc

                if len(X_test_valid) > 0:
                    test_pred = self.pipeline.predict(X_test_valid)
                    test_acc = round(float(accuracy_score(y_test_valid, test_pred)), 4)
                    try:
                        report = classification_report(
                            y_test_valid,
                            test_pred,
                            target_names=[
                                self.classes_[i] for i in sorted(set(y_test_valid))
                            ],
                            output_dict=True,
                        )
                    except Exception:
                        report = {}

        # ── 6. Save model ─────────────────────────────────────────────────────
        _MODEL_PATH.parent.mkdir(exist_ok=True)
        joblib.dump(self.pipeline, _MODEL_PATH)

        self._meta = {
            "classes": self.classes_,
            "n_classes": len(self.classes_),
            "n_train_frames": len(X_train),
            "max_per_class": max_per_class,
            "train_acc": train_acc,
            "test_acc": test_acc,
            "hog_config": {
                "frame_size": _FRAME_SIZE,
                "pixels_per_cell": _HOG_PIXELS,
                "cells_per_block": _HOG_CELLS,
                "orientations": _HOG_ORIENT,
            },
            "trained_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "train_time_seconds": round(t_train, 1),
        }
        _META_PATH.parent.mkdir(exist_ok=True)
        _META_PATH.write_text(json.dumps(self._meta, indent=2))

        # ── 7. Also save the label encoder alongside ──────────────────────────
        _enc_path = _MODEL_PATH.parent / "ucf_crime_encoder.pkl"
        joblib.dump(self.label_encoder, _enc_path)

        print(
            f"✅ Training complete in {t_train:.1f}s  |  train_acc={train_acc}  test_acc={test_acc}"
        )
        print(f"   Model saved → {_MODEL_PATH}")

        return {
            "success": True,
            "classes": self.classes_,
            "n_classes": len(self.classes_),
            "n_train_frames": len(X_train),
            "train_accuracy": train_acc,
            "test_accuracy": test_acc,
            "classification_report": report,
            "train_time_seconds": round(t_train, 1),
            "model_path": str(_MODEL_PATH),
        }

    # ── Inference ──────────────────────────────────────────────────────────────

    def predict_frame(self, image_input: Union[str, "np.ndarray"]) -> dict:
        """
        Predict the crime category for a single frame.

        Args:
            image_input:  File path (str) or grayscale numpy array.

        Returns:
            {
                "label": str,
                "confidence": float,
                "is_anomaly": bool,
                "crime_score": float (0–100),
                "severity": str,
                "aegis_scenario": str,
                "all_scores": {label: score, ...},
            }
        """
        if not self.is_model_available():
            return self._fallback_prediction("Model not trained or not loaded.")

        if not _ml_available():
            return self._fallback_prediction("ML libraries not available.")

        # Extract features — use combined HOG+colour for file paths
        if isinstance(image_input, str):
            feat = _extract_features(image_input)
            if feat is None:
                return self._fallback_prediction(
                    f"Cannot load or extract features from: {image_input}"
                )
        else:
            # numpy array input — use HOG only (no path for colour loading)
            img = image_input
            if CV2_AVAILABLE and cv2 is not None:
                img = cv2.resize(img, _FRAME_SIZE)
            feat = _extract_hog(img)
            if feat is None:
                return self._fallback_prediction("HOG extraction failed.")

        X = np.array([feat], dtype=np.float32)

        try:
            pred_enc = self.pipeline.predict(X)[0]
            label = self.label_encoder.inverse_transform([pred_enc])[0]

            # Compute confidence from decision function
            try:
                df = self.pipeline.decision_function(X)[0]

                if len(self.classes_) == 2:
                    # ── Binary case ───────────────────────────────────────────
                    # SGD binary: positive df → class index 1, negative → class index 0
                    # Confidence = sigmoid(|df|) clamped to [0.5, 1.0]
                    def _sig(x):
                        return 1.0 / (1.0 + np.exp(-float(abs(x))))

                    conf = float(min(max(_sig(df), 0.5), 0.9999))
                    # df < 0 → class 0 wins; df > 0 → class 1 wins
                    if pred_enc == 0:
                        all_scores = {
                            self.classes_[0]: round(conf, 4),
                            self.classes_[1]: round(1 - conf, 4),
                        }
                    else:
                        all_scores = {
                            self.classes_[0]: round(1 - conf, 4),
                            self.classes_[1]: round(conf, 4),
                        }
                else:
                    # ── Multiclass case ───────────────────────────────────────
                    scores_raw = np.array(df, dtype=np.float64)
                    exp_s = np.exp(scores_raw - np.max(scores_raw))
                    scores_norm = exp_s / exp_s.sum()
                    conf = float(scores_norm[pred_enc])
                    all_scores = {
                        cls: round(float(scores_norm[i]), 4)
                        for i, cls in enumerate(self.classes_)
                    }
            except Exception:
                conf = 0.75
                all_scores = {label: 0.75}

        except Exception as e:
            return self._fallback_prediction(f"Inference error: {e}")

        # Handle binary mode labels ("Anomalous"/"Normal") gracefully
        if label == "Anomalous":
            is_anomaly = True
            severity = "HIGH"
            scenario = "accident"
        elif label == "Normal":
            is_anomaly = False
            severity = "NONE"
            scenario = "normal"
        else:
            # Fine-grained label from multiclass mode
            is_anomaly = self.loader.is_anomaly(label)
            severity = self.loader.get_crime_severity(label)
            scenario = self.loader.get_scenario_for_label(label)

        crime_score = round(conf * 100, 1) if is_anomaly else round((1 - conf) * 10, 1)

        return {
            "label": label,
            "confidence": round(conf, 4),
            "is_anomaly": is_anomaly,
            "crime_score": crime_score,
            "severity": severity,
            "aegis_scenario": scenario,
            "all_scores": all_scores,
            "model_available": True,
        }

    def predict_frame_b64(self, b64_string: str) -> dict:
        """
        Predict from a base64-encoded PNG/JPEG image string.
        """
        import base64

        if not NUMPY_AVAILABLE or not CV2_AVAILABLE:
            return self._fallback_prediction("numpy/cv2 not available for b64 decode.")
        try:
            img_bytes = base64.b64decode(b64_string)
            arr = np.frombuffer(img_bytes, dtype=np.uint8)
            img = cv2.imdecode(arr, cv2.IMREAD_GRAYSCALE)
            if img is None:
                return self._fallback_prediction("Could not decode base64 image.")
            return self.predict_frame(img)
        except Exception as e:
            return self._fallback_prediction(f"base64 decode error: {e}")

    # ── Model management ───────────────────────────────────────────────────────

    def is_model_available(self) -> bool:
        """True if a trained model is loaded in memory."""
        return self.pipeline is not None and self.label_encoder is not None

    def get_model_info(self) -> dict:
        """Returns metadata about the currently loaded model."""
        if not self.is_model_available():
            return {
                "model_available": False,
                "model_path": str(_MODEL_PATH),
                "model_file_exists": _MODEL_PATH.exists(),
                "message": "No model loaded. Run train_ucf.py or POST /api/v1/ucf/train to train.",
            }
        return {
            "model_available": True,
            "model_path": str(_MODEL_PATH),
            "model_file_size_mb": (
                round(_MODEL_PATH.stat().st_size / 1e6, 2)
                if _MODEL_PATH.exists()
                else 0
            ),
            **self._meta,
        }

    def _load_model_if_exists(self):
        """Load a previously trained model from disk if available."""
        if not SKLEARN_AVAILABLE or joblib is None:
            return
        try:
            if _MODEL_PATH.exists():
                self.pipeline = joblib.load(_MODEL_PATH)
                enc_path = _MODEL_PATH.parent / "ucf_crime_encoder.pkl"
                if enc_path.exists():
                    self.label_encoder = joblib.load(enc_path)
                    self.classes_ = list(self.label_encoder.classes_)
                if _META_PATH.exists():
                    self._meta = json.loads(_META_PATH.read_text())
                print(
                    f"✅ [UCF Classifier] Loaded pre-trained model from {_MODEL_PATH}"
                )
        except Exception as e:
            logger.warning(f"Could not load pre-trained model: {e}")
            self.pipeline = None
            self.label_encoder = None

    def _fallback_prediction(self, reason: str) -> dict:
        """Returns a safe fallback when prediction is not possible."""
        return {
            "label": "NormalVideos",
            "confidence": 0.0,
            "is_anomaly": False,
            "crime_score": 0.0,
            "severity": "NONE",
            "aegis_scenario": "normal",
            "all_scores": {},
            "model_available": False,
            "fallback_reason": reason,
        }
