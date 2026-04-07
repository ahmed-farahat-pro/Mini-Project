"""Main video processing pipeline - orchestrates detection and cropping."""

import logging
import os
import tempfile
from pathlib import Path

import cv2
import numpy as np
from tqdm import tqdm

from ai_video_crop.config import PipelineConfig
from ai_video_crop.cropper import VideoCropper
from ai_video_crop.detector import ObjectDetector

logger = logging.getLogger(__name__)


class VideoPipeline:
    """End-to-end video processing pipeline.

    Pass in a video, detect unwanted objects, crop/remove them,
    and output the cleaned video.
    """

    def __init__(self, config: PipelineConfig | None = None):
        self.config = config or PipelineConfig()
        self.detector = ObjectDetector(self.config.detection)
        self.cropper = VideoCropper(self.config.crop)

    def process(self, input_path: str, output_path: str | None = None) -> str:
        """Process a video file: detect and crop unwanted regions.

        Args:
            input_path: Path to input video file.
            output_path: Path to output video file. If None, auto-generated.

        Returns:
            Path to the output video file.
        """
        input_path = str(Path(input_path).resolve())
        if not os.path.isfile(input_path):
            raise FileNotFoundError(f"Input video not found: {input_path}")

        if output_path is None:
            stem = Path(input_path).stem
            suffix = f".{self.config.output.output_format}"
            output_path = str(Path(input_path).parent / f"{stem}_cropped{suffix}")

        output_path = str(Path(output_path).resolve())
        logger.info("Processing: %s -> %s", input_path, output_path)

        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open video: {input_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        fourcc = cv2.VideoWriter_fourcc(*self.config.output.codec)
        writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        if not writer.isOpened():
            cap.release()
            raise RuntimeError(f"Cannot create output video: {output_path}")

        logger.info(
            "Video: %dx%d @ %.1f fps, %d frames",
            width, height, fps, total_frames,
        )

        stats = {"total_frames": total_frames, "detections": 0, "frames_with_detections": 0}

        try:
            self._process_frames(cap, writer, total_frames, stats)
        finally:
            cap.release()
            writer.release()

        if self.config.output.keep_audio:
            self._copy_audio(input_path, output_path)

        logger.info(
            "Done! Processed %d frames, %d detections in %d frames",
            stats["total_frames"],
            stats["detections"],
            stats["frames_with_detections"],
        )

        return output_path

    def _process_frames(
        self,
        cap: cv2.VideoCapture,
        writer: cv2.VideoWriter,
        total_frames: int,
        stats: dict,
    ) -> None:
        """Process all frames using batched detection."""
        batch = []
        pbar = tqdm(total=total_frames, desc="Processing frames", unit="frame")

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            batch.append(frame)

            if len(batch) >= self.config.batch_size:
                self._process_batch(batch, writer, stats)
                pbar.update(len(batch))
                batch = []

        if batch:
            self._process_batch(batch, writer, stats)
            pbar.update(len(batch))

        pbar.close()

    def _process_batch(
        self,
        frames: list[np.ndarray],
        writer: cv2.VideoWriter,
        stats: dict,
    ) -> None:
        """Process a batch of frames: detect then crop."""
        all_detections = self.detector.detect_batch(frames)

        for frame, detections in zip(frames, all_detections):
            if detections:
                stats["detections"] += len(detections)
                stats["frames_with_detections"] += 1

            processed = self.cropper.crop_frame(frame, detections)
            writer.write(processed)

    def _copy_audio(self, input_path: str, video_path: str) -> None:
        """Copy audio from original video to the processed output."""
        try:
            import ffmpeg
        except ImportError:
            logger.warning("ffmpeg-python not installed, skipping audio copy")
            return

        try:
            temp_path = video_path + ".tmp.mp4"

            input_video = ffmpeg.input(video_path)
            input_audio = ffmpeg.input(input_path).audio

            ffmpeg.output(
                input_video.video,
                input_audio,
                temp_path,
                vcodec="copy",
                acodec="aac",
                strict="experimental",
            ).overwrite_output().run(quiet=True)

            os.replace(temp_path, video_path)
            logger.info("Audio copied successfully")

        except Exception as e:
            logger.warning("Failed to copy audio: %s", e)
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def get_detection_summary(self, input_path: str, sample_rate: int = 30) -> dict:
        """Analyze a video and return a summary of detected objects without processing.

        Args:
            input_path: Path to input video.
            sample_rate: Check every Nth frame.

        Returns:
            Summary dict with detection statistics.
        """
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open video: {input_path}")

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        class_counts: dict[str, int] = {}
        frames_checked = 0
        frame_idx = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % sample_rate == 0:
                detections = self.detector.detect_frame(frame)
                for det in detections:
                    class_counts[det.class_name] = class_counts.get(det.class_name, 0) + 1
                frames_checked += 1

            frame_idx += 1

        cap.release()

        return {
            "total_frames": total_frames,
            "frames_sampled": frames_checked,
            "fps": fps,
            "duration_seconds": total_frames / fps if fps > 0 else 0,
            "objects_detected": class_counts,
            "total_detections": sum(class_counts.values()),
        }
