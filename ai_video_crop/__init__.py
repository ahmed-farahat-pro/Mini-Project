"""AI Video Crop - Intelligent video cropping and object removal tool."""

__version__ = "1.0.0"

from ai_video_crop.detector import ObjectDetector
from ai_video_crop.cropper import VideoCropper
from ai_video_crop.pipeline import VideoPipeline

__all__ = ["ObjectDetector", "VideoCropper", "VideoPipeline"]
