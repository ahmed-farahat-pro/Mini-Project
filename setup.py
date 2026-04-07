from setuptools import setup, find_packages

setup(
    name="ai-video-crop",
    version="1.0.0",
    description="AI-powered video cropping tool that detects and removes unwanted objects/regions from videos",
    author="Ahmed Farahat",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "opencv-python>=4.8.0",
        "numpy>=1.24.0",
        "torch>=2.0.0",
        "torchvision>=0.15.0",
        "ultralytics>=8.0.0",
        "ffmpeg-python>=0.2.0",
        "pillow>=10.0.0",
        "tqdm>=4.65.0",
        "click>=8.1.0",
        "pydantic>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "ai-video-crop=ai_video_crop.cli:main",
        ],
    },
)
