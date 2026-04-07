# AI Video Crop

AI-powered video cropping tool that uses YOLO object detection to automatically detect and remove unwanted objects from videos. Pass in a video, and the model will crop/remove detected objects and return the cleaned video — making editing easier.

## Features

- **Object Detection**: Uses YOLOv8 to detect objects in video frames
- **Multiple Crop Modes**:
  - `blur` — Gaussian blur over detected regions
  - `black` — Black out detected regions
  - `inpaint` — AI inpainting to fill regions with surrounding context
  - `cut` — Fill with average surrounding color
- **Selective Removal**: Target specific object classes (people, cars, etc.)
- **Batch Processing**: Efficient batched frame processing
- **Audio Preservation**: Keeps original audio in the output
- **Auto-Reframe**: Optionally reframe the video to exclude cropped areas
- **GPU Acceleration**: Supports CUDA and Apple MPS

## Installation

```bash
pip install -e .
```

## Quick Start

```bash
# Blur all detected objects in a video
ai-video-crop process video.mp4

# Black out only people (COCO class 0)
ai-video-crop process video.mp4 --mode black --classes 0

# Inpaint cars and trucks with high confidence
ai-video-crop process video.mp4 --mode inpaint --classes 2,7 --confidence 0.7

# Analyze what objects are in a video (without processing)
ai-video-crop analyze video.mp4

# List all detectable object classes
ai-video-crop list-classes
```

## Python API

```python
from ai_video_crop import VideoPipeline
from ai_video_crop.config import PipelineConfig, DetectionConfig, CropConfig

config = PipelineConfig(
    detection=DetectionConfig(
        confidence_threshold=0.6,
        classes_to_remove=[0],  # Remove people only
    ),
    crop=CropConfig(
        mode="inpaint",
        padding=15,
    ),
)

pipeline = VideoPipeline(config)
output_path = pipeline.process("input.mp4", "output.mp4")
```

## COCO Classes (Common)

| ID | Class    | ID | Class      |
|----|----------|----|------------|
| 0  | person   | 2  | car        |
| 1  | bicycle  | 3  | motorcycle |
| 5  | bus      | 7  | truck      |
| 14 | bird     | 15 | cat        |
| 16 | dog      | 56 | chair      |

Run `ai-video-crop list-classes` for the full list.

## Running Tests

```bash
pip install pytest
pytest tests/
```
