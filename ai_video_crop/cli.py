"""Command-line interface for AI Video Crop."""

import logging
import sys

import click

from ai_video_crop.config import CropConfig, DetectionConfig, OutputConfig, PipelineConfig
from ai_video_crop.pipeline import VideoPipeline


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def main(verbose: bool) -> None:
    """AI Video Crop - Intelligently detect and remove unwanted objects from videos."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


@main.command()
@click.argument("input_video", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), default=None, help="Output video path")
@click.option("--mode", "-m", type=click.Choice(["blur", "black", "inpaint", "cut"]), default="blur", help="Crop mode")
@click.option("--model", default="yolov8n.pt", help="YOLO model name")
@click.option("--confidence", "-c", type=float, default=0.5, help="Detection confidence threshold")
@click.option("--classes", type=str, default=None, help="Comma-separated COCO class IDs to remove (default: all)")
@click.option("--device", type=str, default="auto", help="Device: auto, cpu, cuda, mps")
@click.option("--blur-strength", type=int, default=51, help="Blur kernel size (for blur mode)")
@click.option("--padding", type=int, default=10, help="Padding around detected regions in pixels")
@click.option("--auto-reframe", is_flag=True, help="Automatically reframe to exclude cropped areas")
@click.option("--batch-size", type=int, default=16, help="Batch size for processing")
@click.option("--no-audio", is_flag=True, help="Strip audio from output")
def process(
    input_video: str,
    output: str | None,
    mode: str,
    model: str,
    confidence: float,
    classes: str | None,
    device: str,
    blur_strength: int,
    padding: int,
    auto_reframe: bool,
    batch_size: int,
    no_audio: bool,
) -> None:
    """Process a video: detect and remove unwanted objects.

    Examples:

        # Blur all detected objects
        ai-video-crop process video.mp4

        # Black out only people (COCO class 0)
        ai-video-crop process video.mp4 --mode black --classes 0

        # Inpaint cars and trucks with higher confidence
        ai-video-crop process video.mp4 --mode inpaint --classes 2,7 --confidence 0.7

        # Use a larger model for better accuracy
        ai-video-crop process video.mp4 --model yolov8m.pt
    """
    classes_list = None
    if classes:
        classes_list = [int(c.strip()) for c in classes.split(",")]

    config = PipelineConfig(
        detection=DetectionConfig(
            model_name=model,
            confidence_threshold=confidence,
            classes_to_remove=classes_list,
            device=device,
        ),
        crop=CropConfig(
            mode=mode,
            blur_strength=blur_strength,
            padding=padding,
            auto_reframe=auto_reframe,
        ),
        output=OutputConfig(
            keep_audio=not no_audio,
        ),
        batch_size=batch_size,
    )

    pipeline = VideoPipeline(config)

    click.echo(f"Processing: {input_video}")
    click.echo(f"Mode: {mode} | Model: {model} | Confidence: {confidence}")

    if classes_list:
        click.echo(f"Target classes: {classes_list}")
    else:
        click.echo("Target classes: all detected objects")

    output_path = pipeline.process(input_video, output)
    click.echo(f"\nOutput saved to: {output_path}")


@main.command()
@click.argument("input_video", type=click.Path(exists=True))
@click.option("--model", default="yolov8n.pt", help="YOLO model name")
@click.option("--confidence", "-c", type=float, default=0.5, help="Detection confidence threshold")
@click.option("--sample-rate", type=int, default=30, help="Check every Nth frame")
@click.option("--device", type=str, default="auto", help="Device: auto, cpu, cuda, mps")
def analyze(
    input_video: str,
    model: str,
    confidence: float,
    sample_rate: int,
    device: str,
) -> None:
    """Analyze a video and show what objects are detected (without processing).

    Useful for previewing what will be cropped before running the full process.
    """
    config = PipelineConfig(
        detection=DetectionConfig(
            model_name=model,
            confidence_threshold=confidence,
            device=device,
        ),
    )

    pipeline = VideoPipeline(config)
    summary = pipeline.get_detection_summary(input_video, sample_rate)

    click.echo(f"\nVideo Analysis: {input_video}")
    click.echo(f"Duration: {summary['duration_seconds']:.1f}s ({summary['total_frames']} frames @ {summary['fps']:.1f} fps)")
    click.echo(f"Frames sampled: {summary['frames_sampled']}")
    click.echo(f"Total detections: {summary['total_detections']}")

    if summary["objects_detected"]:
        click.echo("\nDetected objects:")
        for class_name, count in sorted(summary["objects_detected"].items(), key=lambda x: -x[1]):
            click.echo(f"  {class_name}: {count}")
    else:
        click.echo("\nNo objects detected.")


@main.command(name="list-classes")
def list_classes() -> None:
    """List all available COCO class IDs and names."""
    from ultralytics import YOLO

    model = YOLO("yolov8n.pt")
    click.echo("COCO Classes (use --classes with the ID number):\n")
    for class_id, name in sorted(model.names.items()):
        click.echo(f"  {class_id:3d}: {name}")


if __name__ == "__main__":
    main()
