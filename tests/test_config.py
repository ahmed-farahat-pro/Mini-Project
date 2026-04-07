"""Tests for configuration models."""

import pytest
from pydantic import ValidationError

from ai_video_crop.config import CropConfig, DetectionConfig, OutputConfig, PipelineConfig


class TestDetectionConfig:
    def test_defaults(self):
        config = DetectionConfig()
        assert config.model_name == "yolov8n.pt"
        assert config.confidence_threshold == 0.5
        assert config.classes_to_remove is None
        assert config.device == "auto"

    def test_confidence_bounds(self):
        DetectionConfig(confidence_threshold=0.0)
        DetectionConfig(confidence_threshold=1.0)
        with pytest.raises(ValidationError):
            DetectionConfig(confidence_threshold=-0.1)
        with pytest.raises(ValidationError):
            DetectionConfig(confidence_threshold=1.1)


class TestCropConfig:
    def test_defaults(self):
        config = CropConfig()
        assert config.mode == "blur"
        assert config.blur_strength == 51
        assert config.padding == 10
        assert config.auto_reframe is False

    def test_padding_non_negative(self):
        CropConfig(padding=0)
        with pytest.raises(ValidationError):
            CropConfig(padding=-1)


class TestPipelineConfig:
    def test_defaults(self):
        config = PipelineConfig()
        assert config.batch_size == 16
        assert config.max_workers == 4
        assert isinstance(config.detection, DetectionConfig)
        assert isinstance(config.crop, CropConfig)
        assert isinstance(config.output, OutputConfig)
