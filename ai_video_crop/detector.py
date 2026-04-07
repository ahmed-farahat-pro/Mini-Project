"""Object detection module using YOLO for identifying regions to crop."""

import logging
from dataclasses import dataclass

import numpy as np
import torch
from ultralytics import YOLO

from ai_video_crop.config import DetectionConfig

logger = logging.getLogger(__name__)


@dataclass
class Detection:
    """A single detected object in a frame."""

    x1: int
    y1: int
    x2: int
    y2: int
    confidence: float
    class_id: int
    class_name: str

    @property
    def bbox(self) -> tuple[int, int, int, int]:
        return (self.x1, self.y1, self.x2, self.y2)

    @property
    def area(self) -> int:
        return (self.x2 - self.x1) * (self.y2 - self.y1)


class ObjectDetector:
    """YOLO-based object detector for identifying regions to crop from video frames."""

    def __init__(self, config: DetectionConfig | None = None):
        self.config = config or DetectionConfig()
        self._device = self._resolve_device()
        self.model = YOLO(self.config.model_name)
        self.model.to(self._device)
        logger.info("Loaded model %s on device %s", self.config.model_name, self._device)

    def _resolve_device(self) -> str:
        if self.config.device != "auto":
            return self.config.device
        if torch.cuda.is_available():
            return "cuda"
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    def detect_frame(self, frame: np.ndarray) -> list[Detection]:
        """Detect objects in a single frame.

        Args:
            frame: BGR image as numpy array (H, W, C).

        Returns:
            List of Detection objects for regions to crop.
        """
        results = self.model(frame, conf=self.config.confidence_threshold, verbose=False)

        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue

            for i in range(len(boxes)):
                class_id = int(boxes.cls[i].item())

                if self.config.classes_to_remove is not None and class_id not in self.config.classes_to_remove:
                    continue

                x1, y1, x2, y2 = boxes.xyxy[i].cpu().numpy().astype(int)
                confidence = boxes.conf[i].item()
                class_name = self.model.names.get(class_id, str(class_id))

                detections.append(Detection(
                    x1=int(x1), y1=int(y1),
                    x2=int(x2), y2=int(y2),
                    confidence=confidence,
                    class_id=class_id,
                    class_name=class_name,
                ))

        return detections

    def detect_batch(self, frames: list[np.ndarray]) -> list[list[Detection]]:
        """Detect objects in a batch of frames.

        Args:
            frames: List of BGR images as numpy arrays.

        Returns:
            List of detection lists, one per frame.
        """
        results = self.model(frames, conf=self.config.confidence_threshold, verbose=False)

        all_detections = []
        for result in results:
            frame_detections = []
            boxes = result.boxes
            if boxes is not None:
                for i in range(len(boxes)):
                    class_id = int(boxes.cls[i].item())
                    if self.config.classes_to_remove is not None and class_id not in self.config.classes_to_remove:
                        continue

                    x1, y1, x2, y2 = boxes.xyxy[i].cpu().numpy().astype(int)
                    confidence = boxes.conf[i].item()
                    class_name = self.model.names.get(class_id, str(class_id))

                    frame_detections.append(Detection(
                        x1=int(x1), y1=int(y1),
                        x2=int(x2), y2=int(y2),
                        confidence=confidence,
                        class_id=class_id,
                        class_name=class_name,
                    ))
            all_detections.append(frame_detections)

        return all_detections
