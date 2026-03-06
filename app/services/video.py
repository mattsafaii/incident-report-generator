import json
import subprocess
from pathlib import Path

from app.config import ACCEPTED_EXTENSIONS, MAX_DURATION_SECONDS


def get_video_duration(video_path: Path) -> float:
    """Use ffprobe to get video duration in seconds."""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        str(video_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise ValueError(f"ffprobe failed: {result.stderr}")
    info = json.loads(result.stdout)
    return float(info["format"]["duration"])


def validate_video(video_path: Path) -> float:
    """Validate extension and duration. Returns duration in seconds."""
    if video_path.suffix.lower() not in ACCEPTED_EXTENSIONS:
        raise ValueError(f"Unsupported format: {video_path.suffix}")
    duration = get_video_duration(video_path)
    if duration > MAX_DURATION_SECONDS:
        raise ValueError(
            f"Video too long: {duration:.1f}s (max {MAX_DURATION_SECONDS}s)"
        )
    return duration


def extract_frames_1fps(video_path: Path, job_dir: Path) -> int:
    """Extract all frames at 1fps into job_dir. Returns count of frames."""
    job_dir.mkdir(parents=True, exist_ok=True)
    output_pattern = str(job_dir / "frame_%04d.jpg")
    cmd = [
        "ffmpeg", "-i", str(video_path),
        "-vf", "fps=1",
        "-q:v", "2",
        "-y",
        output_pattern,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg frame extraction failed: {result.stderr}")
    return len(list(job_dir.glob("frame_*.jpg")))
