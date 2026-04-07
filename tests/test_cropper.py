"""Tests for the VideoCropper module."""

import numpy as np
import pytest

from ai_video_crop.config import CropConfig
from ai_video_crop.cropper import VideoCropper
from ai_video_crop.detector import Detection


def _make_frame(w: int = 640, h: int = 480) -> np.ndarray:
    """Create a test frame with known pixel values."""
    frame = np.full((h, w, 3), fill_value=128, dtype=np.uint8)
    # Add a colored rectangle in the center
    frame[100:200, 100:200] = [255, 0, 0]  # Blue region
    return frame


def _make_detection(x1=100, y1=100, x2=200, y2=200) -> Detection:
    return Detection(x1=x1, y1=y1, x2=x2, y2=y2, confidence=0.9, class_id=0, class_name="person")


class TestVideoCropper:
    def test_no_detections_returns_copy(self):
        frame = _make_frame()
        cropper = VideoCropper()
        result = cropper.crop_frame(frame, [])
        np.testing.assert_array_equal(result, frame)
        assert result is not frame  # Should be a copy

    def test_blur_mode(self):
        frame = _make_frame()
        cropper = VideoCropper(CropConfig(mode="blur", padding=0))
        det = _make_detection()
        result = cropper.crop_frame(frame, [det])
        # The blurred region should differ from original
        roi_orig = frame[100:200, 100:200]
        roi_result = result[100:200, 100:200]
        assert not np.array_equal(roi_orig, roi_result)

    def test_black_mode(self):
        frame = _make_frame()
        cropper = VideoCropper(CropConfig(mode="black", padding=0))
        det = _make_detection()
        result = cropper.crop_frame(frame, [det])
        # The region should be all zeros
        roi = result[100:200, 100:200]
        assert np.all(roi == 0)

    def test_inpaint_mode(self):
        frame = _make_frame()
        cropper = VideoCropper(CropConfig(mode="inpaint", padding=0))
        det = _make_detection()
        result = cropper.crop_frame(frame, [det])
        # Inpainted region should differ from original blue
        roi = result[100:200, 100:200]
        assert not np.array_equal(roi, frame[100:200, 100:200])

    def test_cut_mode(self):
        frame = _make_frame()
        cropper = VideoCropper(CropConfig(mode="cut", padding=0))
        det = _make_detection()
        result = cropper.crop_frame(frame, [det])
        # The region should be filled with surrounding avg color
        roi = result[100:200, 100:200]
        assert not np.array_equal(roi, frame[100:200, 100:200])

    def test_padding_expands_region(self):
        frame = _make_frame()
        cropper = VideoCropper(CropConfig(mode="black", padding=20))
        det = _make_detection()
        result = cropper.crop_frame(frame, [det])
        # Check that the padded area is also black
        assert np.all(result[80:220, 80:220] == 0)

    def test_multiple_detections(self):
        frame = _make_frame()
        cropper = VideoCropper(CropConfig(mode="black", padding=0))
        dets = [
            _make_detection(50, 50, 100, 100),
            _make_detection(300, 300, 400, 400),
        ]
        result = cropper.crop_frame(frame, dets)
        assert np.all(result[50:100, 50:100] == 0)
        assert np.all(result[300:400, 300:400] == 0)
