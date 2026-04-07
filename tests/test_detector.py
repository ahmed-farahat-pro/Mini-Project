"""Tests for the ObjectDetector module."""

import numpy as np

from ai_video_crop.detector import Detection


class TestDetection:
    def test_bbox_property(self):
        d = Detection(x1=10, y1=20, x2=100, y2=200, confidence=0.9, class_id=0, class_name="person")
        assert d.bbox == (10, 20, 100, 200)

    def test_area_property(self):
        d = Detection(x1=0, y1=0, x2=100, y2=50, confidence=0.9, class_id=0, class_name="person")
        assert d.area == 5000

    def test_area_with_offset(self):
        d = Detection(x1=50, y1=50, x2=150, y2=100, confidence=0.5, class_id=1, class_name="car")
        assert d.area == 5000
