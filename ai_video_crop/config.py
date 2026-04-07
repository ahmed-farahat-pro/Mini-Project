"""Configuration models for the video crop pipeline."""

from typing import Optional
from pydantic import BaseModel, Field


class DetectionConfig(BaseModel):
    """Configuration for the object detection model."""

    model_name: str = Field(default="yolov8n.pt", description="YOLO model to use for detection")
    confidence_threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="Minimum confidence for detections")
    classes_to_remove: Optional[list[int]] = Field(default=None, description="COCO class IDs to detect and crop out. None means all classes.")
    device: str = Field(default="auto", description="Device: 'auto', 'cpu', 'cuda', or 'mps'")


class CropConfig(BaseModel):
    """Configuration for the cropping behavior."""

    mode: str = Field(default="blur", description="Crop mode: 'blur', 'black', 'inpaint', or 'cut'")
    blur_strength: int = Field(default=51, ge=1, description="Gaussian blur kernel size (odd number)")
    inpaint_radius: int = Field(default=5, ge=1, description="Inpainting radius in pixels")
    padding: int = Field(default=10, ge=0, description="Padding around detected regions in pixels")
    auto_reframe: bool = Field(default=False, description="Automatically reframe video to exclude cropped regions")


class OutputConfig(BaseModel):
    """Configuration for the output video."""

    codec: str = Field(default="mp4v", description="Video codec (e.g., 'mp4v', 'XVID', 'H264')")
    output_format: str = Field(default="mp4", description="Output file format")
    keep_audio: bool = Field(default=True, description="Preserve audio from original video")
    quality: int = Field(default=95, ge=1, le=100, description="Output quality (1-100)")


class PipelineConfig(BaseModel):
    """Full pipeline configuration."""

    detection: DetectionConfig = Field(default_factory=DetectionConfig)
    crop: CropConfig = Field(default_factory=CropConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    batch_size: int = Field(default=16, ge=1, description="Number of frames to process in batch")
    max_workers: int = Field(default=4, ge=1, description="Number of parallel workers")
