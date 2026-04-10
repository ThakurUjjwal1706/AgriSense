"""
TFLite Predictor Service
Loads the plant disease TFLite model once at startup and performs fast inference.
Designed to be production-ready and CPU-optimised for embedded/edge deployment.
"""

from __future__ import annotations

import io
import os
import logging
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

# ── Model & Label Paths ─────────────────────────────────────────────────────
_BASE_DIR = Path(__file__).parent.parent / "models"
MODEL_PATH = _BASE_DIR / "model.tflite"
LABELS_PATH = _BASE_DIR / "labels.txt"

# ── Model Input Shape ────────────────────────────────────────────────────────
# PlantVillage-trained models typically use 224x224 RGB
INPUT_SIZE = 224


class TFLitePredictor:
    """
    Singleton-style TFLite inference engine.
    The interpreter and label list are loaded ONCE at class instantiation.
    Reuse a single instance throughout the application lifecycle.
    """

    def __init__(self):
        self._interpreter = None
        self._labels: list[str] = []
        self._input_details = None
        self._output_details = None
        self._input_size: int = INPUT_SIZE
        self._ready: bool = False
        self._load()

    # ── Private Methods ───────────────────────────────────────────────────
    def _load(self) -> None:
        """Load TFLite interpreter and labels file. Called once during init."""
        if not MODEL_PATH.exists():
            logger.error(f"[TFLite] model.tflite not found at {MODEL_PATH}")
            return
        if not LABELS_PATH.exists():
            logger.error(f"[TFLite] labels.txt not found at {LABELS_PATH}")
            return

        try:
            from ai_edge_litert.interpreter import Interpreter  # type: ignore
            self._interpreter = Interpreter(
                model_path=str(MODEL_PATH),
                num_threads=os.cpu_count() or 2,
            )
        except ImportError:
            try:
                import tflite_runtime.interpreter as tflite  # type: ignore
                self._interpreter = tflite.Interpreter(
                    model_path=str(MODEL_PATH),
                    num_threads=os.cpu_count() or 2,
                )
            except ImportError:
                try:
                    import tensorflow as tf  # type: ignore
                    self._interpreter = tf.lite.Interpreter(
                        model_path=str(MODEL_PATH),
                        num_threads=os.cpu_count() or 2,
                    )
                except ImportError:
                    logger.error("[TFLite] No inference backend found. Install: pip install ai-edge-litert")
                    return

        self._interpreter.allocate_tensors()
        self._input_details = self._interpreter.get_input_details()
        self._output_details = self._interpreter.get_output_details()

        # Detect model expected input width from metadata
        shape = self._input_details[0]["shape"]  # [1, H, W, C]
        if len(shape) == 4:
            self._input_size = int(shape[1])

        # Load labels
        with open(LABELS_PATH, "r", encoding="utf-8") as f:
            self._labels = [line.strip() for line in f if line.strip()]

        self._ready = True
        logger.info(
            f"[TFLite] ✅ Model ready — input: {self._input_size}x{self._input_size}, "
            f"{len(self._labels)} classes"
        )

    def _preprocess(self, image_bytes: bytes) -> Optional[np.ndarray]:
        """
        Preprocess raw image bytes into a normalised numpy array
        ready for TFLite inference.

        Returns:
            Float32 array of shape [1, H, W, 3] normalised to [0, 1].
        """
        try:
            img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            img = img.resize((self._input_size, self._input_size), Image.LANCZOS)
            arr = np.array(img, dtype=np.float32) / 255.0  # Normalize to [0, 1]
            return np.expand_dims(arr, axis=0)  # Add batch dimension → [1, H, W, 3]
        except Exception as e:
            logger.error(f"[TFLite] Preprocessing error: {e}")
            return None

    # ── Public API ────────────────────────────────────────────────────────
    @property
    def is_ready(self) -> bool:
        return self._ready

    def predict(self, image_bytes: bytes) -> Tuple[str, float]:
        """
        Run inference on raw image bytes.

        Args:
            image_bytes: Raw bytes of the uploaded image file.

        Returns:
            Tuple of (class_label: str, confidence: float)

        Raises:
            RuntimeError: If the model is not loaded or inference fails.
        """
        if not self._ready:
            raise RuntimeError("TFLite model is not loaded. Check model.tflite and labels.txt paths.")

        tensor = self._preprocess(image_bytes)
        if tensor is None:
            raise ValueError("Image preprocessing failed. Ensure the file is a valid image.")

        # Check if model expects quantized (uint8) or float input
        input_dtype = self._input_details[0]["dtype"]
        if input_dtype == np.uint8:
            tensor = (tensor * 255).astype(np.uint8)

        self._interpreter.set_tensor(self._input_details[0]["index"], tensor)
        self._interpreter.invoke()

        output_data = self._interpreter.get_tensor(self._output_details[0]["index"])
        scores = output_data[0]  # Shape: [num_classes]

        # Handle quantized output
        if self._output_details[0]["dtype"] == np.uint8:
            scale, zero_point = self._output_details[0]["quantization"]
            scores = (scores.astype(np.float32) - zero_point) * scale

        predicted_idx = int(np.argmax(scores))
        confidence = float(scores[predicted_idx])

        if predicted_idx >= len(self._labels):
            raise IndexError(f"Predicted index {predicted_idx} is out of range for {len(self._labels)} labels.")

        label = self._labels[predicted_idx]
        return label, round(confidence, 4)


# ── Module-level singleton ───────────────────────────────────────────────────
# Loaded once when this module is first imported
_predictor: Optional[TFLitePredictor] = None


def get_predictor() -> TFLitePredictor:
    """Return the global TFLite predictor, initialising if needed."""
    global _predictor
    if _predictor is None:
        _predictor = TFLitePredictor()
    return _predictor


def predict_disease(image_bytes: bytes) -> Tuple[str, float]:
    """
    Top-level convenience function for route handlers.

    Args:
        image_bytes: Raw uploaded image bytes.

    Returns:
        (label: str, confidence: float)
    """
    return get_predictor().predict(image_bytes)
