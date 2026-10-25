"""Compose already-generated talking-head videos into a simple scene."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


TARGET_WIDTH = 512
TARGET_HEIGHT = 512
TARGET_FPS = 25


def _ffmpeg_path() -> str:
    """Use system FFmpeg when available, otherwise the embedded-Python copy."""
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError as error:
        raise RuntimeError("FFmpeg was not found on PATH and imageio_ffmpeg is unavailable.") from error


def build_two_person_command(
    video1_path: str | Path,
    video2_path: str | Path,
    output_path: str | Path,
    *,
    layout: str = "side_by_side",
) -> list[str]:
    """Build the FFmpeg command for a fixed, normalized two-person scene."""
    if layout != "side_by_side":
        raise ValueError("Only layout='side_by_side' is supported by this prototype.")

    # Normalize both sources to 512x512 RGB video at 25 FPS, preserving each
    # person's aspect ratio with black padding.  `shortest=1` on both filters
    # safely limits the result to the shorter source.  Both audio tracks are
    # mixed at equal normalized level and likewise stop at the shorter input.
    filter_graph = (
        "[0:v]fps=25,scale=512:512:force_original_aspect_ratio=decrease,"
        "pad=512:512:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1[v0];"
        "[1:v]fps=25,scale=512:512:force_original_aspect_ratio=decrease,"
        "pad=512:512:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1[v1];"
        "[v0][v1]hstack=inputs=2:shortest=1[v];"
        "[0:a]aresample=48000[a0];[1:a]aresample=48000[a1];"
        "[a0][a1]amix=inputs=2:duration=shortest:normalize=1[a]"
    )
    return [
        _ffmpeg_path(), "-y",
        "-i", str(video1_path), "-i", str(video2_path),
        "-filter_complex", filter_graph,
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p", "-r", str(TARGET_FPS),
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
        "-shortest", str(output_path),
    ]


def compose_two_person_scene(
    video1_path: str | Path,
    video2_path: str | Path,
    output_path: str | Path,
    layout: str = "side_by_side",
) -> Path:
    """Combine two existing MP4s into a playable side-by-side MP4.

    This function only invokes FFmpeg.  It never loads FLOAT, generates video,
    or accesses the ComfyUI installation.
    """
    video1_path = Path(video1_path).expanduser().resolve()
    video2_path = Path(video2_path).expanduser().resolve()
    output_path = Path(output_path).expanduser().resolve()
    for label, path in (("Person 1 video", video1_path), ("Person 2 video", video2_path)):
        if not path.is_file():
            raise FileNotFoundError(f"{label} was not found: {path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    command = build_two_person_command(video1_path, video2_path, output_path, layout=layout)
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg composition failed:\n{result.stderr}")
    if not output_path.is_file() or output_path.stat().st_size == 0:
        raise RuntimeError(f"FFmpeg completed without producing an MP4: {output_path}")
    return output_path
