"""Video frame cropping module - applies crop/removal operations to detected regions."""

import logging

import cv2
import numpy as np

from ai_video_crop.config import CropConfig
from ai_video_crop.detector import Detection

logger = logging.getLogger(__name__)


class VideoCropper:
    """Applies cropping operations to video frames based on detected regions."""

    def __init__(self, config: CropConfig | None = None):
        self.config = config or CropConfig()

    def crop_frame(self, frame: np.ndarray, detections: list[Detection]) -> np.ndarray:
        """Apply crop/removal to a single frame for all detected regions.

        Args:
            frame: BGR image as numpy array (H, W, C).
            detections: List of detected objects to remove.

        Returns:
            Processed frame with detected regions removed/cropped.
        """
        if not detections:
            return frame.copy()

        result = frame.copy()
        h, w = result.shape[:2]

        for det in detections:
            x1 = max(0, det.x1 - self.config.padding)
            y1 = max(0, det.y1 - self.config.padding)
            x2 = min(w, det.x2 + self.config.padding)
            y2 = min(h, det.y2 + self.config.padding)

            if self.config.mode == "blur":
                result = self._apply_blur(result, x1, y1, x2, y2)
            elif self.config.mode == "black":
                result = self._apply_black(result, x1, y1, x2, y2)
            elif self.config.mode == "inpaint":
                result = self._apply_inpaint(result, x1, y1, x2, y2)
            elif self.config.mode == "cut":
                result = self._apply_cut(result, x1, y1, x2, y2)

        if self.config.auto_reframe and detections:
            result = self._auto_reframe(result, detections, w, h)

        return result

    def _apply_blur(self, frame: np.ndarray, x1: int, y1: int, x2: int, y2: int) -> np.ndarray:
        """Blur the detected region."""
        k = self.config.blur_strength
        if k % 2 == 0:
            k += 1
        roi = frame[y1:y2, x1:x2]
        blurred = cv2.GaussianBlur(roi, (k, k), 0)
        frame[y1:y2, x1:x2] = blurred
        return frame

    def _apply_black(self, frame: np.ndarray, x1: int, y1: int, x2: int, y2: int) -> np.ndarray:
        """Black out the detected region."""
        frame[y1:y2, x1:x2] = 0
        return frame

    def _apply_inpaint(self, frame: np.ndarray, x1: int, y1: int, x2: int, y2: int) -> np.ndarray:
        """Inpaint the detected region using surrounding context."""
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        mask[y1:y2, x1:x2] = 255
        frame = cv2.inpaint(frame, mask, self.config.inpaint_radius, cv2.INPAINT_TELEA)
        return frame

    def _apply_cut(self, frame: np.ndarray, x1: int, y1: int, x2: int, y2: int) -> np.ndarray:
        """Fill the region with the average color of the surrounding area."""
        h, w = frame.shape[:2]
        expand = 20
        sx1 = max(0, x1 - expand)
        sy1 = max(0, y1 - expand)
        sx2 = min(w, x2 + expand)
        sy2 = min(h, y2 + expand)

        surrounding_mask = np.ones((sy2 - sy1, sx2 - sx1), dtype=bool)
        inner_y1 = y1 - sy1
        inner_x1 = x1 - sx1
        inner_y2 = y2 - sy1
        inner_x2 = x2 - sx1
        surrounding_mask[inner_y1:inner_y2, inner_x1:inner_x2] = False

        surrounding_region = frame[sy1:sy2, sx1:sx2]
        if surrounding_mask.any():
            avg_color = surrounding_region[surrounding_mask].mean(axis=0).astype(np.uint8)
        else:
            avg_color = np.array([0, 0, 0], dtype=np.uint8)

        frame[y1:y2, x1:x2] = avg_color
        return frame

    def _auto_reframe(self, frame: np.ndarray, detections: list[Detection], w: int, h: int) -> np.ndarray:
        """Reframe the video to focus on the area without detected objects."""
        all_x1 = [d.x1 for d in detections]
        all_x2 = [d.x2 for d in detections]

        if min(all_x1) < w // 2:
            crop_x1 = max(d.x2 for d in detections if d.x1 < w // 2)
            crop_x2 = w
        else:
            crop_x1 = 0
            crop_x2 = min(all_x1)

        crop_x1 = max(0, crop_x1)
        crop_x2 = min(w, crop_x2)

        if crop_x2 - crop_x1 < w // 4:
            return frame

        cropped = frame[0:h, crop_x1:crop_x2]
        return cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LANCZOS4)
